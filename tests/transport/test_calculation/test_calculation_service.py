from unittest.mock import patch

import pytest

from apps.transport.services.calculation_service import apply_schedule


@pytest.mark.django_db
def test_apply_schedule_updates_calculation_fields(calculation):
    fake_result = {
        "schedule_table": [
            ["Day 1", "Driving (A → B)", 120],
            ["Day 1", "Break (45 min)", 45],
        ],
        "total_km": 500,
        "total_drive_time_minutes": 120,
        "total_break_time_minutes": 45,
        "total_rest_time_minutes": 660,
        "total_other_work_time_minutes": 30,
        "days_for_one_trip": 2,
    }

    with patch("apps.transport.services.calculation_service.generate_schedule", return_value=fake_result):
        apply_schedule(calculation)

    assert calculation.total_km == 500
    assert calculation.total_drive_time_minutes == 120
    assert calculation.total_break_time_minutes == 45
    assert calculation.total_rest_time_minutes == 660
    assert calculation.total_other_work_time_minutes == 30
    assert calculation.schedule is not None
    assert "Day 1: Driving (A → B)" in calculation.schedule
