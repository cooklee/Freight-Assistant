from apps.transport.services.schedule_builder import generate_schedule

def apply_schedule(calculation):
    route = calculation.route
    # TODO (perf): Upewnij się, że caller robi select_related('route') + prefetch_related('route__stops'),
    # TODO (perf): jeśli apply_schedule jest wołane w pętli (np. batch), żeby uniknąć N+1.

    stops = list(route.stops.order_by("stop_number"))
    # TODO (data,bug): potencjalna wtopa bo tutaj stops moze byc 0,1 ? jesli tak to w generate schedule mozesz dostać wartość ujemną co daje moze wywalić appke nie chce mi sie az tak wgryzać w algorytm zeby dotrzeć do tego

    driver_count = 2 if calculation.driver_2 else 1

    result = generate_schedule(stops=stops, driver_count=driver_count)
    # TODO (robustness): Jeśli generate_schedule może rzucać wyjątki (np. brak danych), warto je tu złapać
    # TODO (robustness): i ustawić calculation.schedule na informację o błędzie albo propagować kontrolowany wyjątek.

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
        # TODO (i18n): Znak "–" jest OK, ale jeśli chcesz ASCII-only w logach/eksportach, użyj "-" ktoś generował kod za pomoca chata :D.

    calculation.schedule = "\n".join(rows)