from apps.core.utils.google_maps import get_distance_duration


def to_minutes(hours):
    return int(hours * 60)


def generate_schedule(stops, avg_speed_kph=80, month_days=30, driver_count=1):
    """
    It builds a work schedule for the driver/drivers based on the list of stops
    and travel times between them, taking into account EU regulations.
    Returns a dict from:
    - schedule_table
    - total_km
    - total_drive_time_minutes
    - days_for_one_trip
    - possible_monthly_trips
    - total_break_time_minutes
    - total_rest_time_minutes
    - total_work_time_minutes
    """

    schedule = []
    current_day = 1
    daily_drive_minutes = 0
    daily_total_minutes = 0
    used_10h_days = 0
    weekly_drive_minutes = 0
    biweekly_drive_minutes = 0
    total_drive_time = 0
    total_km = 0
    day_of_week = 1
    total_break_time = 0
    total_rest_time = 0
    total_work_time = 0
    current_driver = 1
    shared_drive_minutes = 0

    if driver_count == 2:
        MAX_SHARED_DRIVE = to_minutes(20)
        REST_DAILY = to_minutes(9)
    else:
        MAX_DAILY_DRIVE = to_minutes(9)
        EXTENDED_DAILY_DRIVE = to_minutes(10)
        MAX_DAILY_TOTAL = to_minutes(15)
        REST_DAILY = to_minutes(11)

    MAX_WEEKLY_DRIVE = to_minutes(56)
    MAX_2WEEK_DRIVE = to_minutes(90)
    BREAK_AFTER_4_5 = to_minutes(0.75)
    WEEKLY_REST = to_minutes(45)

    i = 0
    while i < len(stops) - 1:
        origin = stops[i]
        destination = stops[i + 1]

        km, time_min = get_distance_duration(origin.location, destination.location)
        if km is None or time_min is None:
            i += 1
            continue

        total_km += km
        travel_time = int(time_min)
        remaining_travel = travel_time

        while remaining_travel > 0:
            if driver_count == 2:
                shared_remaining = MAX_SHARED_DRIVE - shared_drive_minutes
                segment = min(to_minutes(4.5), remaining_travel, shared_remaining)
            else:
                today_limit = (
                    EXTENDED_DAILY_DRIVE
                    if used_10h_days < 2
                    else MAX_DAILY_DRIVE
                )
                daily_remaining_drive = today_limit - daily_drive_minutes
                segment = min(to_minutes(4.5), remaining_travel, daily_remaining_drive)

            if segment <= 0 or (
                    driver_count == 1 and daily_total_minutes >= MAX_DAILY_TOTAL
            ):
                schedule.append([f"Day {current_day}", "Rest", REST_DAILY])
                total_rest_time += REST_DAILY
                current_day += 1
                daily_drive_minutes = 0
                daily_total_minutes = 0
                shared_drive_minutes = 0
                day_of_week += 1
                continue

            driver_label = f"Driver {current_driver}" if driver_count == 2 else ""
            schedule.append([
                f"Day {current_day}",
                f"{driver_label} Driving ({origin.location} → {destination.location})",
                segment
            ])
            current_driver = 2 if current_driver == 1 else 1

            remaining_travel -= segment
            daily_drive_minutes += segment
            daily_total_minutes += segment
            shared_drive_minutes += segment if driver_count == 2 else 0
            weekly_drive_minutes += segment
            biweekly_drive_minutes += segment
            total_drive_time += segment
            total_work_time += segment

            if segment == to_minutes(4.5) and driver_count == 1:
                schedule.append([f"Day {current_day}", "Pause", BREAK_AFTER_4_5])
                daily_total_minutes += BREAK_AFTER_4_5
                total_break_time += BREAK_AFTER_4_5
                total_work_time += BREAK_AFTER_4_5

            if driver_count == 1 and daily_drive_minutes >= EXTENDED_DAILY_DRIVE:
                used_10h_days += 1

        stop_type = destination.stop_type
        participated = destination.driver_participates

        if stop_type in ["LOADING", "UNLOADING", "FINAL_STOP"]:
            extra_time = to_minutes(2) if participated else to_minutes(1)
        elif stop_type in ["PARTIAL_LOADING", "PARTIAL_UNLOADING"]:
            extra_time = to_minutes(1.5) if participated else to_minutes(1)
        else:
            extra_time = 0

        if extra_time > 0:
            schedule.append([
                f"Day {current_day}",
                "Administration/Physical work", extra_time
            ])
            daily_total_minutes += extra_time
            total_work_time += extra_time

        if daily_total_minutes >= to_minutes(15):
            schedule.append([f"Day {current_day}", "Rest", REST_DAILY])
            total_rest_time += REST_DAILY
            current_day += 1
            daily_drive_minutes = 0
            daily_total_minutes = 0
            shared_drive_minutes = 0
            day_of_week += 1

        if weekly_drive_minutes >= MAX_WEEKLY_DRIVE or day_of_week > 6:
            schedule.append([f"Day {current_day}", "Weekly rest", WEEKLY_REST])
            total_rest_time += WEEKLY_REST
            current_day += 2
            weekly_drive_minutes = 0
            day_of_week = 1
            daily_drive_minutes = 0
            daily_total_minutes = 0
            shared_drive_minutes = 0

        if biweekly_drive_minutes > MAX_2WEEK_DRIVE:
            schedule.append([f"Day {current_day}", "2-WEEK LIMIT EXCEEDED", 0])
            break

        i += 1

    schedule.append([f"Day {current_day}", "Rest", REST_DAILY])
    total_rest_time += REST_DAILY
    total_work_time += REST_DAILY

    days_for_trip = current_day
    weeks_used = days_for_trip / 7
    possible_trips = 0
    if weeks_used <= 4 and biweekly_drive_minutes <= MAX_2WEEK_DRIVE:
        rest_buffer_days = 2 if driver_count == 1 else 1

        if days_for_trip >= 6:
            recovery_days = 2
        elif days_for_trip >= 3:
            recovery_days = 1
        else:
            recovery_days = 0

        trip_total_days = days_for_trip + rest_buffer_days + recovery_days
        possible_trips = int(month_days / trip_total_days)

    return {
        "schedule_table": schedule,
        "total_km": int(total_km),
        "total_drive_time_minutes": int(total_drive_time),
        "days_for_one_trip": days_for_trip,
        "possible_monthly_trips": possible_trips,
        "total_break_time_minutes": int(total_break_time),
        "total_rest_time_minutes": int(total_rest_time),
        "total_work_time_minutes": int(total_work_time)
    }
