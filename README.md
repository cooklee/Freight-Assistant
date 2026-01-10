# Freight Assistant 🚛
![Python](https://img.shields.io/badge/python-3.x-blue)
![Django](https://img.shields.io/badge/django-5.x-green)

**Freight Assistant** is a Django-based web application designed to support freight forwarders
and dispatchers in planning and validating truck routes according to **EU driving time regulations (EC 561/2006)**.

The core goal of the project is to **automatically generate a realistic transport schedule**, including:

- driving time,
- mandatory breaks,
- daily and weekly rests,
- loading, unloading and administrative work,

allowing a dispatcher to estimate a full transport plan **in seconds instead of 1–2 hours of manual calculations**.

---

## 🧠 Problem statement

In real-life freight forwarding:

- route planning must comply with strict EU regulations,
- manual calculations are time-consuming and error-prone,
- even small mistakes may lead to fines or invalid schedules.

**Freight Assistant automates this process**, producing a dispatcher-friendly, step-by-step schedule
that can be reliably used for operational planning and decision-making.

---

## ⚙️ Key features

✅ User-based data isolation (multi-user system)  
✅ Route creation with multiple stops (loading, unloading, partial operations)  
✅ Google Maps integration for distance and travel time calculation  
✅ Automatic schedule generation respecting:
- 4.5h continuous driving limit,
- mandatory 45-minute breaks,
- daily and weekly rest requirements,
- single-driver and double-driver crews  
✅ Clear breakdown of:
- driving time,
- breaks,
- rests,
- other work (loading / unloading / administration)  
✅ PDF export of transport schedules  
✅ Live client-side filtering on list views (no page reloads)

---

## 🧮 Schedule builder – high-level overview

1. A route is split into legs between consecutive stops.
2. Each leg’s distance and driving time is fetched from Google Maps.
3. Driving time is accumulated **across multiple legs** until the 4h30 limit is reached.
4. Mandatory breaks are inserted automatically.
5. Loading/unloading is treated as **work time**, not rest.
6. Daily and weekly limits are enforced using planner-oriented heuristics.
7. The final output is a readable, step-by-step schedule compliant with EU regulations.

The scheduling logic is implemented as a **dedicated service layer**, separated from views and templates,
making it testable, readable and easy to extend.

---

## 🏗 Architecture & code structure

This project is a **second iteration**, written fully from scratch.
Compared to the previous version, it introduces a significantly cleaner architecture:

- clear separation between:
  - views (HTTP layer),
  - services (business logic),
  - templates (presentation),
- modular Django app structure,
- minimal logic in views,
- business rules encapsulated in dedicated service classes,
- extensive use of Django class-based views and mixins,
- test coverage for key business logic.

This architecture improves maintainability, testability and overall code clarity.

---

## 🖼 Application screenshots

Screenshots below present the current development version of the application.

### 📊 Calculations list
Overview of transport calculations with route and distance summary.

![Calculations list](screenshots/calculations_list.png)

---

### 🧮 Calculation details & schedule
Detailed calculation view with:
- total distance,
- driving time,
- breaks,
- rests,
- step-by-step EU-compliant schedule.

![Calculation detail](screenshots/calculation_detail.png)

---

### 🚚 Transport orders list
Transport orders overview including customer, carrier, distance and profit.

![Transport orders list](screenshots/transport_orders_list.png)

---

### 📄 Transport order details
Detailed transport order view with pricing and profitability breakdown.

![Transport order detail](screenshots/transport_order_detail.png)

> Dates visible in screenshots come from development seed data (`populate.py`) and are used for demonstration purposes only.

---

## 🏗 Tech stack

- Python 3
- Django
- PostgreSQL
- Google Maps Platform:
  - Distance Matrix API
  - Places Autocomplete API
- HTML / Django Templates
- Tailwind CSS + DaisyUI
- Pytest
- WeasyPrint (PDF generation)

A full list of dependencies is available in `requirements.txt`.

---

## 📌 Project status

The project is **feature-complete for its current scope** and represents a finished, working solution.
Further development would focus on refinements and additional business scenarios rather than core functionality.

This repository serves as a **portfolio project**, showcasing:
- real-world business logic,
- EU regulation-driven constraints,
- clean Django architecture,
- separation of concerns,
- incremental development and refactoring.

---

## 🚀 How to run locally (development)

### 1) Clone the repository
```bash
git clone https://github.com/Shizol01/Freight-Assistant.git
cd Freight-Assistant
```

### 2) Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows (PowerShell)
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Environment configuration
Create a `.env` file in the project root directory:

```env
SECRET_KEY=your-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Database
DB_NAME=freight_assistant
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Populate test user
TEST_USERNAME=test_user
TEST_USER_PASS=test1234
```

> `GOOGLE_MAPS_API_KEY` is required for:
> - Google Distance Matrix API (distance & travel time)
> - Google Places Autocomplete API (validated stop locations)

### 5) Database setup
Make sure PostgreSQL is running and the database exists.

```bash
python manage.py migrate
```

### 6) Populate demo data (recommended)
```bash
python manage.py populate
```

This command creates demo data:
- users (including test user),
- customers and branches,
- carriers and drivers,
- routes with stops,
- transport orders,
- calculations with schedules (uses Google Distance Matrix API) ,
- demo messaging conversations.

### 7) Tailwind (required for UI styling)
```bash
python manage.py tailwind install
python manage.py tailwind build
```

### 8) Run development server
```bash
python manage.py runserver
```

Open in browser:
```
http://127.0.0.1:8000/
```

### 9) Login credentials (after populate)
```
username: test_user
password: test1234
```

### Notes
- Django 5 + PostgreSQL
- User-based data isolation
- Dates visible in the UI come from development seed data (`populate.py`)


## 👤 Author

Created by **Shizol01**  
Python / Django Developer


