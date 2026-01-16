# Freight Assistant – audit projektu (całościowy)

> Zakres: przegląd architektury, jakości kodu, bezpieczeństwa, testowalności i gotowości produkcyjnej na podstawie zawartości repozytorium z pliku `Freight-Assistant.zip`.

## TL;DR

Projekt ma **dobry „kręgosłup” architektoniczny**: modularne aplikacje Django, czytelne widoki, sensowne formularze, a najważniejsze – **logika planowania czasu pracy kierowców jest wydzielona do warstwy usług i ma sensowne testy jednostkowe**.

Największe ryzyka na dziś to:

1. **Bezpieczeństwo i konfiguracja produkcyjna** (m.in. `ALLOWED_HOSTS=['*']`, brak twardych wymuszeń na `SECRET_KEY`, „produkcyjne” ustawienia w praktyce są szkicem).
2. **Testy i konfiguracja DB** – `pytest.ini` wskazuje `fa_core.settings.base`, a `base.py` wymaga Postgresa z ENV; w praktyce to utrudnia uruchamianie testów lokalnie/CI.
3**Obsługa błędów Google Maps** – awaria API powoduje „ciche” pominięcie odcinka (plan dalej się generuje, ale może być niepoprawny bez ostrzeżenia).

Jeśli to ma być projekt portfolio: super. Jeśli ma iść do produkcji: warto zrobić „hardening” konfiguracji, poprawić multi-tenancy, dopracować testy/CI i dodać wyraźne ścieżki błędów.

---

## 1) Przegląd architektury

#
### Co jest do poprawy

- W kilku miejscach widać **niedokończone/porzucone elementy**:
  - `apps/transport/services/pdf_export.py` ma placeholder `render_to_string(...)` i wygląda na nieużywany.
- Logika uprawnień jest implementowana „ręcznie” (filtry w `get_object_or_404`, `filter(user=request.user)`), co jest OK, ale:
  - łatwo o pomyłkę w przyszłości,
  - warto rozważyć wspólny mixin/utility do owner-checków.

---

## 2) Model danych i „multi-user isolation”

### Stan obecny

- Dobre: `Route`, `Calculation`, `TransportOrder` mają pole `user` i w `transport` widać konsekwentne filtrowanie po `user=request.user`.
- Problem: `Carrier`, `Customer`, `CustomerBranch`, `Driver` **nie mają powiązania z użytkownikiem**.
  - Widoki `company/*` i `drivers/*` używają `Model.objects.all()`.
  - To oznacza, że w środowisku wieloużytkownikowym każdy użytkownik:
    - widzi dane wszystkich,
    - może edytować/usuwać globalne rekordy.

### Ryzyko

- To jest realny „data leak” w kontekście multi-user.
- Unikalność `nip` (NIP jest `unique=True`) robi się globalna, więc „tenant A” może zablokować „tenant B”.

### Rekomendacja

W zależności od intencji projektu:

1) **Jeśli to ma być multi-tenant per dispatcher (izolacja pełna)**:
- Dodaj `user = ForeignKey(User, ...)` do `Carrier`, `Customer`, `CustomerBranch`, `Driver`.
- Wszędzie w widokach i querysetach filtruj po `user=request.user`.
- Zmień unikalność `nip` na unikalność per user (np. `UniqueConstraint(fields=['user','nip'])`).

2) **Jeśli dane firmowe mają być współdzielone (jedna organizacja)**:
- Zmień komunikację w README i w UI: nie obiecuj „user-based isolation” dla tych encji.
- Dodaj role/uprawnienia (np. moderator/admin) i ogranicz edycję do wybranych.

---

## 3) Logika planowania czasu pracy (EU schedule builder)

### Mocne strony

- `schedule_builder.generate_schedule()` jest:
  - w jednym miejscu,
  - opisana komentarzami,
  - **testowana** (jest zestaw testów obejmujący m.in. przerwy po 4h30, brak przerwy na końcu, weekly rest, biweekly warning, tryb 2 kierowców).
- Dobrze, że rozróżniono:
  - przerwę wymaganą po 4h30 jazdy,
  - pracę inną niż jazda (załadunek/rozładunek/admin), która **nie resetuje licznika jazdy**.

### Słabsze miejsca / ryzyka domenowe

- Algorytm jest opisany jako „heurystyczny” (i to jest OK), ale warto doprecyzować w README:
  - które reguły są „twardo zgodne”,
  - które są uproszczeniem.
- Aktualnie, gdy Google Maps zwróci błąd (`None, None`), odcinek jest **pomijany bez ostrzeżenia**.
  - To może generować plan, który wygląda poprawnie, ale jest niepoprawny (brak kilometrów/minut w środku trasy).

### Rekomendacje

- Zamiast `continue` przy braku danych z Google:
  - zwróć błąd do użytkownika (np. walidacja route: „nie udało się pobrać danych dla odcinka X→Y”),
  - albo oznacz wynik jako „NIEKOMPLETNY” i pokaż alert w UI.
- Wydziel „konfigurację limitów” do obiektu/klasy (łatwiejsze rozszerzenia/reguły per kraj/typ przewozu).
- Rozważ zapis wyniku planowania jako struktury (JSON / tabela) zamiast tekstu `schedule`:
  - łatwiej o późniejsze filtrowanie, eksport, wykresy, integracje.

---

## 4) Integracja z Google Maps (Distance Matrix)

### Stan

- `apps/core/utils/google_maps.py` robi bezpośredni `requests.get(..., timeout=10)`.
- Brak cache.

### Ryzyka

- Koszty / quota / rate limiting.
- Wydajność – dla wielu odcinków robisz wiele requestów sekwencyjnie.

### Rekomendacje

- Dodaj cache (minimum):
  - per (origin,destination) w DB lub w cache (Redis/Memcached), z TTL.
- Rozważ batch query:
  - Distance Matrix pozwala na wiele destinations/origins w jednym zapytaniu.
- Rozszerz obsługę błędów:
  - loguj przyczyny (statusy API),
  - zwracaj informację użytkownikowi.

---

## 5) Bezpieczeństwo i konfiguracja środowisk

### Najważniejsze problemy

- `fa_core/settings/base.py`:
  - `DEBUG = True` (w bazie),
  - `SECRET_KEY` ma default `''` (pusty),
  - `ALLOWED_HOSTS = []`.
- `fa_core/settings/prod.py`:
  - `DEBUG = False`, ale `ALLOWED_HOSTS = ['*']` (bardzo zły pomysł produkcyjnie).
- Operacje mutujące przez GET:
  - `ProfileImageDeleteView` usuwa zdjęcie profile przez `GET` (powinno być `POST` + CSRF).
- W paczce zip znajduje się **`.env` z danymi** (hasła/username). Nawet jeśli to „tylko dev”, to:
  - łatwo to przypadkiem zacommitować,
  - w portfolio lepiej tego unikać.

### Rekomendacje „hardening”

- Ustawienia:
  - przenieś `DEBUG` do `dev.py`, a `base.py` ustaw bezpiecznie (`DEBUG=False` lub z ENV).
  - `SECRET_KEY` wymagany: jeśli brak w ENV -> raise Exception.
  - `ALLOWED_HOSTS` z ENV; w produkcji **konkretny host**.
  - dodaj typowe settingi security dla prod: `CSRF_TRUSTED_ORIGINS`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS` (w zależności od deploy).
- Zmień `ProfileImageDeleteView` na `post()` i dodaj template z potwierdzeniem/CSRF.
- Dopilnuj, by `.env` nigdy nie trafiał do repo (w praktyce: usuń z zip/portfolio, trzymaj `env example`).

---

## 6) Testy, jakość i ergonomia developmentu

### Co działa

- Jest sporo testów widoków i formularzy.
- Logika schedule builder ma sensowne pokrycie.

### Problemy

- `pytest.ini` wskazuje `DJANGO_SETTINGS_MODULE = fa_core.settings.base`.
  - a `base.py` jest skonfigurowane pod Postgresa i oczekuje ENV.
  - to utrudnia uruchomienie testów „z marszu” (np. na CI i u rekrutera).

### Rekomendacje

- Dodaj `fa_core/settings/test.py`:
  - sqlite in-memory (albo Postgres w docker-compose, ale wtedy dodaj compose).
  - szybsze testy, zero dodatkowych wymagań.
- Dodaj prosty pipeline CI (GitHub Actions):
  - `pip install -r requirements.txt`
  - `python -m pytest`
  - (opcjonalnie) `flake8`.
- Rozdziel zależności:
  - `requirements.txt` (runtime)
  - `requirements-dev.txt` (pytest, flake8, faker, itd.).

---

## 7) Utrzymanie kodu (clean code / spójność)

### Spójność i techniczne detale

- W wielu miejscach używany jest `django.contrib.auth.models.User` zamiast `get_user_model()`.
  - To ogranicza możliwość przejścia na custom user w przyszłości.
- Widać trochę „martwego kodu” i drobnych no-opów:
  - `apps/transport/services/pdf_export.py` placeholder,
  - `DriverUpdateView.post`: `driver.carrier = driver.carrier`.

### Rekomendacje

- Konsekwentnie używaj `get_user_model()` w modelach i formach tam, gdzie to ma sens.
- Usuń/napraw nieużywane pliki (albo dodaj TODO z uzasadnieniem).
- Rozważ lekkie ujednolicenie stylu:
  - Black + isort (opcjonalnie),
  - typowanie tylko tam, gdzie daje wartość (np. w services).

---

## 8) Plan działań (priorytety)

### P0 – szybkie poprawki (1–2h)

- [ ] Usuń `.env` z paczki/projektu portfolio (zostaw tylko `env example`).
- [ ] Zmień `ProfileImageDeleteView` na POST + CSRF.
- [ ] Popraw `prod.py`: `ALLOWED_HOSTS` z ENV, bez `'*'`.
- [ ] Wymuś `SECRET_KEY` (brak => błąd startu).
- [ ] Dodaj ostrzeżenie w UI, gdy Google Maps zwróci `None` (nie generuj „cichego” planu).

### P1 – poprawa jakości i CI (0.5–1 dnia)

- [ ] Dodaj `settings/test.py` + zaktualizuj `pytest.ini`.
- [ ] Dodaj GitHub Actions (testy + lint).
- [ ] Podziel requirements na runtime/dev.

### P2 – decyzja o multi-tenancy (1–2 dni)

- [ ] Wybierz model: pełna izolacja per user **albo** wspólna baza danych firmy.
- [ ] Dopasuj modele i widoki (`company`, `drivers`) do wybranego wariantu.
- [ ] Uzupełnij README, żeby nie było rozjazdu obietnic vs. implementacji.

### P3 – rozwój domenowy (kolejne iteracje)

- [ ] Cache/batching dla Google Distance Matrix.
- [ ] Zapis schedule jako struktura (JSON) + lepszy eksport/filtry.
- [ ] Więcej scenariuszy testowych dla edge-case’ów EU (jeśli produktowo potrzebne).

---
