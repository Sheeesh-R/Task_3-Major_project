# HSC Study Planner – Task Organiser App

A Flask-based web application for HSC students to organise tasks, track assessment marks, and predict ATAR scores using UAC scaling data.

## Features

- **User Authentication** – Register, login, logout with secure password hashing (Werkzeug)
- **Task Management** – Full CRUD for tasks with due dates, priorities (High/Medium/Low), statuses, categories, and subject association
- **Subject Organisation** – Create/edit/delete subjects with units (1/2) and target marks
- **Assessment Tracker** – Record weighted assessment results per subject; auto-calculates running estimated mark
- **ATAR Prediction** – Polynomial-regression ATAR estimator using built-in UAC scaling tables; saves prediction history with confidence intervals
- **Dashboard** – Subject cards with progress, filterable/sortable task list, academic calendar, overview statistics
- **Mobile-First Responsive UI** – Clean academic theme (navy/gold), touch-friendly controls, adaptive breakpoints
- **Security** – CSRF protection (Flask-WTF), parameterised SQL, environment-based secrets, password hashing

## Requirements

- Python 3.10+
- Virtual environment (`venv` or `virtualenv`)
- Dependencies listed in `requirements.txt`:
  ```
  Flask
  Flask-WTF
  python-dotenv
  Werkzeug
  ```

## Getting Started

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Task_Organiser_App

# 2. Create & activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create a .env file in Task_Organiser_App/ with:
# SECRET_KEY=your-strong-random-secret
# LOG_LEVEL=INFO

# 5. Run the development server
python run.py
```

Open http://127.0.0.1:5000 – you will be redirected to `/login` if not authenticated.

## Project Structure

```
Task_Organiser_App/
├── Task_Organiser/
│   ├── app.py                 # Flask app factory, routes, filters
│   ├── db.py                  # DB connection, schema init/migration, indexes
│   ├── atar_data.py           # UAC scaling data & ATAR calculation engine
│   ├── task_schema.sql        # Base SQLite schema (users, tasks, subjects, etc.)
│   ├── schema_updates.sql     # Incremental migrations (adds columns/tables)
│   ├── static/css/            # Custom stylesheets
│   ├── templates/             # Jinja2 templates (base, index, forms, etc.)
│   └── instance/taskmanager.db # SQLite database (auto-created)
├── run.py                     # App entry point
├── requirements.txt
└── tests/
    └── test_atar_data.py      # Unit tests for ATAR calculation
```

## Database Schema (Key Tables)

| Table | Purpose |
|-------|---------|
| `users` | Authentication (username, password_hash, email) |
| `subjects` | User-defined subjects (name, units, target_mark) |
| `tasks` | Tasks linked to subject/user (due_date, priority, status, category) |
| `categories` | Task categories (Work, Study, Personal – seeded) |
| `assessment_results` | Weighted assessment marks per subject |
| `atar_predictions` | Historical ATAR predictions with aggregate & uncertainty fields |

Indexes exist on `user_id`, `subject_id`, `status`, `priority` for query performance.

## Running Tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Docker (Optional)

```bash
docker build -t hsc-study-planner .
docker run -p 5000:5000 --env-file .env hsc-study-planner
```

## Security Patch & Automation Notes

- **SECRET_KEY** – No longer hard-coded; loaded from `.env` / deployment config via `python-dotenv`. Fallback logs a warning.
- **Password Hashing** – Replaced custom SHA-256 with `werkzeug.security.generate_password_hash` / `check_password_hash` (PBKDF2 + salt).
- **CSRF Protection** – Enabled `Flask-WTF` `CSRFProtect`; all POST forms include `{{ csrf_field() }}`; meta token injected in `base.html`.
- **SQL Safety** – All queries use parameterised statements (`?` placeholders); no string interpolation.
- **Dead Code Removal** – Deleted unused `static/js/scripts.js` and the priority widget endpoint.
- **Test Coverage** – `tests/test_atar_data.py` validates scaling lookup, aggregate calculation, and ATAR conversion (4 tests passing).
- **CI Ready** – GitHub Actions workflow (`.github/workflows/ci.yml`) installs deps, runs unit tests, and lints Python on every push/PR.

## License

MIT – feel free to use, modify, and distribute.

