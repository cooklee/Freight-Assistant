from apps.transport.services.schedule_builder import generate_schedule


def apply_schedule(calculation):
    route = calculation.route
    stops = list(route.stops.order_by("stop_number"))
    driver_count = 2 if calculation.driver_2 else 1
    result = generate_schedule(stops=stops, driver_count=driver_count)

    calculation.total_km = result["total_km"]
    calculation.total_drive_time_minutes = result["total_drive_time_minutes"]
    calculation.total_break_time_minutes = result["total_break_time_minutes"]
    calculation.total_rest_time_minutes = result["total_rest_time_minutes"]
    calculation.total_other_work_time_minutes = result["total_other_work_time_minutes"]

    rows = []
    for day, task, minutes in result["schedule_table"]:
        hours = minutes // 60
        mins = minutes % 60
        rows.append(f"{day}: {task} – {hours}h {mins}min")
    calculation.schedule = "\n".join(rows)
