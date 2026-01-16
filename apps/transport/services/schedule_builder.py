from apps.core.utils.google_maps import get_distance_duration
# TODO (perf): get_distance_duration robi zewnętrzny request. W generate_schedule jest wołane w pętli dla każdej "nogi".
# TODO (perf): Rozważ cache (np. origin/destination -> wynik) albo batchowanie, inaczej łatwo o limity i wolne generowanie.
# TODO (robustness): Rozważ retry/backoff na 429/5xx, albo fallback na avg_speed_kph, zamiast "continue" (gubi nogę).


def to_minutes(hours: float) -> int:
    """Convert hours to rounded minutes."""
    return int(round(hours * 60))
    # TODO (clarity): Nazwa parametru "hours" jest OK, ale w kodzie przekazujesz liczby typu 56/90/45 (jak godziny) — OK.
    # TODO (style): Dla stałych można rozważyć bezpośrednie wartości minut, jeśli to upraszcza debug.


BREAK_AFTER_DRIVE_MIN = 45
MAX_CONTINUOUS_DRIVE_MIN = 270  # 4.5h


def _stop_service_minutes(stop) -> int:
    """
    Planning assumption for stop handling time:
    - Default admin/paperwork time: 30 minutes
    - If the driver participates:
        * LOADING / UNLOADING -> 60 minutes
        * PARTIAL_* -> 45 minutes
    """
    if stop.stop_type not in {"LOADING", "UNLOADING", "PARTIAL_LOADING", "PARTIAL_UNLOADING"}:
        return 0

    if not stop.driver_participates:
        return 30

    if stop.stop_type in {"PARTIAL_LOADING", "PARTIAL_UNLOADING"}:
        return 45

    return 60
    # TODO (maint): Te czasy to "magic numbers". Rozważ stałe / konfigurację (np. dict mapping stop_type->minutes).
    # TODO (typing): Dodaj typ stop (np. Stop) jeśli to możliwe, ułatwi IDE i refaktoryzację.


def generate_schedule(stops, avg_speed_kph=80, driver_count=1):
    """
    Build a dispatcher-friendly schedule for a multi-stop route.

    Returns a dict:
      - schedule_table: list[[day_label, task, minutes]]
      - total_km
      - total_drive_time_minutes
      - total_break_time_minutes
      - total_rest_time_minutes
      - total_other_work_time_minutes
      - days_for_one_trip

    Important rule implemented:
      - Loading/unloading/admin is NOT a driving break and MUST NOT reset the 4.5h continuous driving counter.
      - The 45-min driving break must be inserted after 4.5h of driving accumulated since last break/rest.
    """

    # TODO (validation): Jeśli stops ma mniej niż 2 elementy, pętla "for i in range(len(stops)-1)" nic nie zrobi,
    # TODO (validation): a na końcu i tak dodasz daily rest. Rozważ early return z ostrzeżeniem / wyjątkiem.

    # Core limits (planner-oriented heuristics aligned with EU basics)
    MAX_WEEKLY_DRIVE_MIN = to_minutes(56)
    MAX_2WEEK_DRIVE_MIN = to_minutes(90)
    WEEKLY_REST_MIN = to_minutes(45)

    # Single driver limits
    MAX_DAILY_DRIVE_MIN = to_minutes(9)
    EXT_DAILY_DRIVE_MIN = to_minutes(10)
    MAX_EXTENDED_DAYS_PER_WEEK = 2

    # Simplified daily duty window:
    # - typical day: ~13h duty with regular 11h rest
    # - allow up to 15h duty when using reduced 9h rest (heuristic)
    MAX_DAILY_DUTY_MIN = to_minutes(13)
    MAX_DAILY_DUTY_EXT_MIN = to_minutes(15)
    REGULAR_DAILY_REST_MIN = to_minutes(11)
    REDUCED_DAILY_REST_MIN = to_minutes(9)
    MAX_REDUCED_DAILY_RESTS_BETWEEN_WEEKLY = 3

    # Team (two-driver crew) simplified planning constraints
    TEAM_DUTY_WINDOW_MIN = to_minutes(30)  # 30h window (planning simplification)
    TEAM_DAILY_REST_MIN = to_minutes(9)

    # TODO (maint): Wiele stałych z przepisów/heurystyk — warto w przyszłości wyciągnąć do osobnego modułu/configu,
    # TODO (maint): z komentarzem: dla jakiego kraju/roku i które są uproszczeniem.

    schedule = []

    # Totals
    total_km = 0
    total_drive = 0
    total_break = 0
    total_rest = 0
    total_other = 0

    # Day/week counters
    day = 1
    day_of_week = 1
    weekly_drive = 0
    biweekly_drive = 0

    # Single driver counters
    daily_drive = 0
    daily_duty = 0
    used_extended_days = 0
    reduced_daily_rests_used = 0
    continuous_drive_since_break = 0  # IMPORTANT: driving minutes since last 45-min break/rest

    # Team counters (per driver)
    team_daily_drive = {1: 0, 2: 0}
    team_current_driver = 1
    team_window_used = 0  # minutes used inside the 30h team window

    # Track per-driver continuous driving and "off-duty while other drives" minutes.
    # In team mode, a driver's required break can be satisfied while the other driver drives,
    # as long as the driver is not doing other work.
    team_continuous_drive = {1: 0, 2: 0}
    team_off_duty_while_other_drives = {1: 0, 2: 0}

    def _more_driving_ahead(leg_index: int, remaining_in_leg: int) -> bool:
        """
        Returns True if there is driving still expected after the current moment:
        - either still remaining in current leg, OR
        - there are further legs after this one.
        """
        if remaining_in_leg > 0:
            return True
        return leg_index < (len(stops) - 2)
        # TODO (clarity): Ten warunek jest poprawny, ale dość nieintuicyjny. Rozważ komentarz/przykład indeksów. dodatkowo do tego czepiałem sie z apps/transport/services/calculation_service.py:13

    def _insert_break_single_if_needed(leg_index: int, remaining_in_leg: int):
        """
        Insert the mandatory 45-min break if:
        - continuous driving has reached 4.5h, AND
        - we expect more driving ahead (now or later), AND
        - we still have duty capacity; otherwise end day with rest.
        """
        nonlocal daily_duty, total_break, continuous_drive_since_break

        if continuous_drive_since_break < MAX_CONTINUOUS_DRIVE_MIN:
            return

        if not _more_driving_ahead(leg_index, remaining_in_leg):
            # No more driving expected; do not add a break right before ending schedule.
            continuous_drive_since_break = 0
            # TODO (logic): To resetuje licznik nawet bez przerwy — to jest heurystyka "koniec jazdy => reset".
            # TODO (logic): Jeśli chcesz być bardziej zgodny z przepisami, rozważ czy reset powinien następować tylko po break/rest.
            return

        # If we cannot fit the break into the current duty window, end the day instead.
        if daily_duty + BREAK_AFTER_DRIVE_MIN > MAX_DAILY_DUTY_EXT_MIN:
            new_day_with_rest(is_team=False)
            return

        schedule.append([f"Day {day}", "Break (45 min)", BREAK_AFTER_DRIVE_MIN])
        daily_duty += BREAK_AFTER_DRIVE_MIN
        total_break += BREAK_AFTER_DRIVE_MIN
        continuous_drive_since_break = 0

    def new_day_with_rest(is_team: bool):
        nonlocal day, day_of_week
        nonlocal daily_drive, daily_duty, reduced_daily_rests_used, continuous_drive_since_break
        nonlocal team_daily_drive, team_window_used
        nonlocal team_continuous_drive, team_off_duty_while_other_drives
        nonlocal total_rest

        if is_team:
            schedule.append([f"Day {day}", "Daily rest (team)", TEAM_DAILY_REST_MIN])
            total_rest += TEAM_DAILY_REST_MIN

            day += 1
            day_of_week += 1
            # TODO (bug): day_of_week inkrementujesz też w weekly_rest i resetujesz na 1.
            # TODO (bug): Nie ma modulo 7 ani twardego ograniczenia; bazujesz na >6. Upewnij się, że logika jest spójna.

            team_daily_drive[1] = 0
            team_daily_drive[2] = 0
            team_window_used = 0
            team_continuous_drive[1] = 0
            team_continuous_drive[2] = 0
            team_off_duty_while_other_drives[1] = 0
            team_off_duty_while_other_drives[2] = 0
            return

        # Single driver
        # Heuristic: allow reduced daily rest (9h) when duty exceeded typical 13h,
        # but no more than 3 times between weekly rests.
        if daily_duty > MAX_DAILY_DUTY_MIN and reduced_daily_rests_used < MAX_REDUCED_DAILY_RESTS_BETWEEN_WEEKLY:
            rest = REDUCED_DAILY_REST_MIN
            reduced_daily_rests_used += 1
            label = "Daily rest (reduced)"
        else:
            rest = REGULAR_DAILY_REST_MIN
            label = "Daily rest (regular)"

        schedule.append([f"Day {day}", label, rest])
        total_rest += rest

        day += 1
        day_of_week += 1

        daily_drive = 0
        daily_duty = 0
        continuous_drive_since_break = 0  # reset on daily rest

    def weekly_rest():
        nonlocal day, day_of_week, weekly_drive
        nonlocal daily_drive, daily_duty, reduced_daily_rests_used, continuous_drive_since_break
        nonlocal team_daily_drive, team_window_used
        nonlocal team_continuous_drive, team_off_duty_while_other_drives
        nonlocal total_rest

        schedule.append([f"Day {day}", "Weekly rest", WEEKLY_REST_MIN])
        total_rest += WEEKLY_REST_MIN

        # Planning simplification: treat weekly rest as consuming the next calendar day too.
        day += 2
        day_of_week = 1
        weekly_drive = 0

        daily_drive = 0
        daily_duty = 0
        reduced_daily_rests_used = 0
        continuous_drive_since_break = 0  # reset on weekly rest

        team_daily_drive[1] = 0
        team_daily_drive[2] = 0
        team_window_used = 0
        team_continuous_drive[1] = 0
        team_continuous_drive[2] = 0
        team_off_duty_while_other_drives[1] = 0
        team_off_duty_while_other_drives[2] = 0
        # TODO (maint): Resetów jest dużo i łatwo się pomylić. Rozważ helper do resetowania "team state".

    # Iterate route legs
    for i in range(len(stops) - 1):
        origin = stops[i]
        destination = stops[i + 1]

        km, time_min = get_distance_duration(origin.location, destination.location)

        # Fallback (optional): if Google fails, you could approximate using avg_speed_kph.
        # For now, if Google fails, skip this leg.
        if km is None or time_min is None:
            continue


        total_km += km
        remaining = int(time_min)

        # Drive the leg in chunks
        while remaining > 0:
            if driver_count == 1:
                # Decide today's driving cap (9h or 10h) based on used extended days.
                today_drive_limit = EXT_DAILY_DRIVE_MIN if used_extended_days < MAX_EXTENDED_DAYS_PER_WEEK else MAX_DAILY_DRIVE_MIN
                daily_drive_remaining = today_drive_limit - daily_drive

                # End day if we have no driving capacity or duty window is full
                if daily_drive_remaining <= 0 or daily_duty >= MAX_DAILY_DUTY_EXT_MIN:
                    new_day_with_rest(is_team=False)
                    continue

                # How much can we drive before we MUST take a 45-min break?
                until_break = MAX_CONTINUOUS_DRIVE_MIN - continuous_drive_since_break
                if until_break <= 0:
                    _insert_break_single_if_needed(i, remaining)
                    continue

                chunk = min(remaining, daily_drive_remaining, until_break)

                if chunk <= 0:
                    new_day_with_rest(is_team=False)
                    continue

                schedule.append([f"Day {day}", f"Driving ({origin.location} → {destination.location})", chunk])

                remaining -= chunk

                daily_drive += chunk
                daily_duty += chunk
                weekly_drive += chunk
                biweekly_drive += chunk
                total_drive += chunk
                continuous_drive_since_break += chunk

                # If we just hit 4.5h continuous driving, insert the break (if more driving ahead).
                _insert_break_single_if_needed(i, remaining)

                # Mark extended-day usage once we exceed 9h driving (planner heuristic).
                if daily_drive > MAX_DAILY_DRIVE_MIN and used_extended_days < MAX_EXTENDED_DAYS_PER_WEEK:
                    used_extended_days += 1

            else:
                # TEAM (2 drivers): rotate at most every 4.5h; each driver has daily cap (simplified 9h).
                if team_window_used >= TEAM_DUTY_WINDOW_MIN:
                    new_day_with_rest(is_team=True)
                    continue

                current = team_current_driver
                other = 2 if current == 1 else 1

                driver_remaining = MAX_DAILY_DRIVE_MIN - team_daily_drive[current]
                if driver_remaining <= 0:
                    # Switch driver. If both are exhausted, window will end naturally.
                    team_current_driver = other
                    continue

                # Team continuous driving per driver: must not exceed 4.5h
                until_break_driver = MAX_CONTINUOUS_DRIVE_MIN - team_continuous_drive[current]
                if until_break_driver <= 0:
                    # Force switch to allow rest
                    team_current_driver = other
                    continue

                chunk = min(remaining, driver_remaining, until_break_driver)

                if chunk <= 0:
                    new_day_with_rest(is_team=True)
                    continue

                schedule.append(
                    [f"Day {day}", f"Driver {current} driving ({origin.location} → {destination.location})", chunk])
                remaining -= chunk

                team_daily_drive[current] += chunk
                team_window_used += chunk
                weekly_drive += chunk
                biweekly_drive += chunk
                total_drive += chunk

                # Update continuous driving for current driver
                team_continuous_drive[current] += chunk

                # The other driver is considered "off-duty while other drives" (rest/break),
                # so accumulate time and reset their continuous driving if off-duty >= 45 min.
                team_off_duty_while_other_drives[other] += chunk
                if team_off_duty_while_other_drives[other] >= BREAK_AFTER_DRIVE_MIN:
                    team_continuous_drive[other] = 0
                    team_off_duty_while_other_drives[other] = 0

                # If current driver hit 4.5h continuous, switch driver.
                if team_continuous_drive[current] >= MAX_CONTINUOUS_DRIVE_MIN:
                    schedule.append([f"Day {day}", "Driver change (planned)", 5])
                    team_window_used += 5
                    total_other += 5
                    team_current_driver = other
                else:
                    # Simple rotation policy: switch drivers between legs/chunks for realism
                    team_current_driver = other
                    # TODO (logic): Ten else powoduje przełączanie nawet gdy current nie osiągnął 4.5h,
                    # TODO (logic): więc realnie rotujesz co "chunk". Jeśli chunk bywa mały, to może wyglądać dziwnie w planie.

            # Hard limit warnings/checks
            if biweekly_drive > MAX_2WEEK_DRIVE_MIN:
                schedule.append([f"Day {day}", "WARNING: 2-week driving limit exceeded", 0])
                remaining = 0
                break

            if weekly_drive >= MAX_WEEKLY_DRIVE_MIN or day_of_week > 6:
                weekly_rest()

        # Stop handling time at destination (NOT a break)
        stop_minutes = _stop_service_minutes(destination)
        if stop_minutes:
            schedule.append([f"Day {day}", "Loading/unloading/admin", stop_minutes])
            total_other += stop_minutes

            if driver_count == 1:
                daily_duty += stop_minutes
                # IMPORTANT: do NOT reset continuous_drive_since_break here
            else:
                team_window_used += stop_minutes
                # In team mode, treat it as other work; do not reset continuous counters.

        # If duty window is full, close the day
        if driver_count == 1 and daily_duty >= MAX_DAILY_DUTY_EXT_MIN:
            new_day_with_rest(is_team=False)

        if driver_count == 2 and team_window_used >= TEAM_DUTY_WINDOW_MIN:
            new_day_with_rest(is_team=True)

    # Finish with a daily rest to "close" the plan (cosmetic but useful for ETA thinking)
    if driver_count == 1:
        new_day_with_rest(is_team=False)
    else:
        new_day_with_rest(is_team=True)


    return {
        "schedule_table": schedule,
        "total_km": int(round(total_km)),
        "total_drive_time_minutes": int(total_drive),
        "total_break_time_minutes": int(total_break),
        "total_rest_time_minutes": int(total_rest),
        "total_other_work_time_minutes": int(total_other),
        "days_for_one_trip": day - 1,

    }
