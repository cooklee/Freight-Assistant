from unittest.mock import patch

import pytest

from apps.transport.services.schedule_builder import (
    generate_schedule,
    _stop_service_minutes,
    MAX_CONTINUOUS_DRIVE_MIN,
    to_minutes,
)


class DummyStop:
    def __init__(self, location, stop_type="LOADING", driver_participates=False):
        self.location = location
        self.stop_type = stop_type
        self.driver_participates = driver_participates


def _patch_legs(legs):
    """
    legs: list of (km, minutes) returned sequentially for each route leg.
    """
    legs = legs.copy()

    def fake_get_distance_duration(origin, destination):
        return legs.pop(0)

    return fake_get_distance_duration


def test_stop_service_minutes_non_service_stop_is_zero():
    stop = DummyStop("X", stop_type="START_FROM_BASE", driver_participates=True)
    assert _stop_service_minutes(stop) == 0


def test_stop_service_minutes_default_admin_30_when_no_participation():
    stop = DummyStop("X", stop_type="LOADING", driver_participates=False)
    assert _stop_service_minutes(stop) == 30


def test_stop_service_minutes_partial_with_participation_is_45():
    stop = DummyStop("X", stop_type="PARTIAL_LOADING", driver_participates=True)
    assert _stop_service_minutes(stop) == 45


def test_stop_service_minutes_full_with_participation_is_60():
    stop = DummyStop("X", stop_type="UNLOADING", driver_participates=True)
    assert _stop_service_minutes(stop) == 60


@pytest.mark.django_db
def test_google_none_leg_is_skipped_and_plan_still_closes_with_rest():
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "FINAL_STOP"),
    ]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            return_value=(None, None)
    ):
        result = generate_schedule(stops=stops, driver_count=1)

    assert result["total_drive_time_minutes"] == 0
    assert result["total_rest_time_minutes"] >= to_minutes(9)
    assert result["schedule_table"]


@pytest.mark.django_db
def test_break_inserted_after_4h30_across_multiple_legs_and_loading_does_not_reset():
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "LOADING", driver_participates=False),
        DummyStop("C", "FINAL_STOP"),
    ]

    legs = [(300, 216), (200, 149)]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs(legs)
    ):
        result = generate_schedule(stops=stops, driver_count=1)

    tasks = [row[1] for row in result["schedule_table"]]
    assert any("Break (45 min)" in t for t in tasks), "Expected mandatory 45-min break after 4.5h driving"
    assert result["total_break_time_minutes"] >= 45


@pytest.mark.django_db
def test_no_break_inserted_when_no_more_driving_ahead():
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "FINAL_STOP"),
    ]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs([(400, MAX_CONTINUOUS_DRIVE_MIN)])
    ):
        result = generate_schedule(stops=stops, driver_count=1)

    tasks = [row[1] for row in result["schedule_table"]]
    assert not any("Break (45 min)" in t for t in tasks), "Break should not be inserted at end-of-route"
    assert result["total_break_time_minutes"] == 0


@pytest.mark.django_db
def test_if_break_cannot_fit_in_duty_window_end_day_instead_of_break():
    """
    Covers branch in _insert_break_single_if_needed:
      if daily_duty + 45 > MAX_DAILY_DUTY_EXT_MIN -> new_day_with_rest()
    We force daily_duty close to 15h and then hit break condition while still having driving ahead.
    """
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "LOADING", driver_participates=True),
        DummyStop("C", "FINAL_STOP"),
    ]

    legs = [(500, 271), (10, 10)]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs(legs)
    ):
        result = generate_schedule(stops=stops, driver_count=1)

    tasks = [row[1] for row in result["schedule_table"]]
    assert any(t.startswith("Daily rest") for t in tasks)


@pytest.mark.django_db
def test_weekly_rest_triggered_by_day_of_week_over_6():
    stops = [DummyStop(f"P{i}", "START_FROM_BASE" if i == 0 else "FINAL_STOP") for i in range(9)]
    stops[-1].stop_type = "FINAL_STOP"

    legs = [(500, 540)] * (len(stops) - 1)

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs(legs)
    ):
        result = generate_schedule(stops=stops, driver_count=1)

    tasks = [row[1] for row in result["schedule_table"]]
    assert "Weekly rest" in tasks


@pytest.mark.django_db
def test_biweekly_warning_branch_added_and_stops_current_leg():
    """
    Covers:
      if biweekly_drive > 90h: append warning and break out
    """
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "FINAL_STOP"),
    ]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs([(4000, 5500)])
    ):
        result = generate_schedule(stops=stops, driver_count=1)

    tasks = [row[1] for row in result["schedule_table"]]
    assert any("WARNING: 2-week driving limit exceeded" in t for t in tasks)


@pytest.mark.django_db
def test_team_mode_switches_driver_and_adds_driver_change_planned():
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "FINAL_STOP"),
    ]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs([(500, 300)])
    ):
        result = generate_schedule(stops=stops, driver_count=2)

    tasks = [row[1] for row in result["schedule_table"]]
    assert any("Driver change (planned)" in t for t in tasks)
    assert result["total_other_work_time_minutes"] >= 5


@pytest.mark.django_db
def test_team_mode_stop_service_adds_other_work_not_break():
    stops = [
        DummyStop("A", "START_FROM_BASE"),
        DummyStop("B", "LOADING", driver_participates=False),
        DummyStop("C", "FINAL_STOP"),
    ]

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=_patch_legs([(100, 60), (100, 60)])
    ):
        result = generate_schedule(stops=stops, driver_count=2)

    tasks = [row[1] for row in result["schedule_table"]]
    assert "Loading/unloading/admin" in tasks
    assert result["total_other_work_time_minutes"] >= 30
    assert not any("Break (45 min)" in t for t in tasks)
