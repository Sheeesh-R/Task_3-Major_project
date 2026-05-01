# HSC Study Planner — Upgrade Plan

## Overview

Transform the existing Task Manager into an HSC Study Planner with ATAR prediction. The app will let students track tasks per subject, input assessment marks, and receive a Polynomial Regression-based ATAR estimate.

---

## 1. UI Overhaul — Professional & Formal Design

### Design Direction
Replace the current purple gradient aesthetic with a clean, academic look. Think government portal meets university dashboard — high contrast, structured, minimal decoration.

### Colour Palette
```css
:root {
    --primary: #1a3a5c;        /* Deep navy */
    --primary-light: #2c5282;  /* Medium navy */
    --accent: #c8972b;         /* Gold/amber — academic feel */
    --success: #276749;        /* Dark green */
    --danger: #9b2335;         /* Deep red */
    --bg: #f4f6f9;             /* Off-white page background */
    --card-bg: #ffffff;
    --text-primary: #1a202c;
    --text-secondary: #4a5568;
    --border: #cbd5e0;
}
```

### Changes to `base.html`
- Replace gradient navbar with a solid `--primary` navy bar
- Add a thin gold (`--accent`) bottom border on the navbar
- Switch font from `Space Grotesk` to `Inter` only — remove decorative fonts
- Replace all gradient buttons with flat, bordered buttons
- Remove card hover `translateY` animations — keep subtle `box-shadow` only
- Add a persistent **sidebar** layout (desktop) with subject navigation links
- Footer: dark navy background, simple copyright line

### Changes to `index.html`
- Replace the gradient "Task Dashboard" hero text with a plain `<h1>` in `--primary`
- Remove the overview cards' gradient icons — use simple coloured borders instead
- Make the calendar collapsible section open by default on desktop
- Add a **subject tab bar** at the top of the task list (see Section 3)

### Changes to `add_task.html` and `edit_task.html`
- Remove the gradient card header — replace with a plain white card with a navy left border (`border-left: 4px solid var(--primary)`)
- Form labels: sentence case, not uppercase
- Buttons: flat style with border, no gradient

### Changes to `login.html` and `register.html`
- Centre card on page with a navy header strip (not gradient)
- Add the app name/logo above the card
- Remove the circular icon decoration

---

## 2. Database Changes

### New Tables

Add these to `task_schema.sql`:

```sql
-- Subjects the student is enrolled in
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,                  -- e.g. "Mathematics Advanced"
    units INTEGER NOT NULL DEFAULT 2,    -- 1 or 2 unit subject
    target_mark INTEGER,                 -- Student's personal target (0-100)
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- HSC assessment results per subject
CREATE TABLE assessment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assessment_name TEXT NOT NULL,       -- e.g. "Trial Exam", "Task 2"
    weight REAL NOT NULL,                -- Percentage weight e.g. 30.0
    raw_mark REAL NOT NULL,              -- Mark achieved
    max_mark REAL NOT NULL,              -- Mark out of
    date_recorded TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Modify `tasks` Table
Add a `subject_id` column to link tasks to subjects:
```sql
ALTER TABLE tasks ADD COLUMN subject_id INTEGER REFERENCES subjects(id);
```

> Remove `category_id` from tasks or keep it as optional — subjects replace categories as the primary organiser.

### ATAR Scaling Data
Hardcode a Python dictionary in a new file `atar_scaling.py`. This stores the UAC scaling parameters per subject. Example structure:

```python
# Source: UAC Historical Scaling Reports
# Polynomial coefficients mapping raw HSC mark -> scaled mark (approx)
SCALING_DATA = {
    "Mathematics Extension 2": {
        "units": 2,
        "scale_factor": 1.18,   # scaled marks generally higher than raw
        "coefficients": [0.0003, 0.85, 8.2]  # for np.polyval
    },
    "Mathematics Advanced": {
        "units": 2,
        "scale_factor": 1.05,
        "coefficients": [0.0001, 0.92, 4.1]
    },
    "English Advanced": {
        "units": 2,
        "scale_factor": 1.0,
        "coefficients": [0.0, 1.0, 0.0]
    },
    "Chemistry": {
        "units": 2,
        "scale_factor": 1.08,
        "coefficients": [0.0002, 0.88, 6.5]
    },
    "Physics": {
        "units": 2,
        "scale_factor": 1.07,
        "coefficients": [0.0002, 0.87, 6.0]
    },
    "Biology": {
        "units": 2,
        "scale_factor": 0.98,
        "coefficients": [0.0, 0.95, 1.5]
    },
    "Legal Studies": {
        "units": 2,
        "scale_factor": 0.95,
        "coefficients": [0.0, 0.93, 2.0]
    },
    "Economics": {
        "units": 2,
        "scale_factor": 1.06,
        "coefficients": [0.0001, 0.90, 5.0]
    },
    "Business Studies": {
        "units": 2,
        "scale_factor": 0.92,
        "coefficients": [0.0, 0.91, 1.0]
    },
    "English Standard": {
        "units": 2,
        "scale_factor": 0.88,
        "coefficients": [0.0, 0.88, 0.0]   # scales down — lower than Eng Adv
    },
    "Mathematics Standard 2": {
        "units": 2,
        "scale_factor": 0.90,
        "coefficients": [0.0, 0.89, 1.0]
    },
    "Mathematics Extension 1": {
        "units": 1,                          # 1 unit subject (counted on top of Maths Adv)
        "scale_factor": 1.14,
        "coefficients": [0.0002, 0.88, 7.8]  # strong scaling, sits between Adv and Ext 2
    },
    "Chemistry": {
        "units": 2,
        "scale_factor": 1.08,
        "coefficients": [0.0002, 0.88, 6.5]
    },
    "Software Engineering": {
        "units": 2,
        "scale_factor": 1.03,
        "coefficients": [0.0001, 0.91, 3.5]
    },
    "English Extension 1": {
        "units": 1,                          # 1 unit subject (taken on top of Eng Adv)
        "scale_factor": 1.09,
        "coefficients": [0.0001, 0.92, 5.0]
    },
    "Design and Technology": {
        "units": 2,
        "scale_factor": 0.96,
        "coefficients": [0.0, 0.94, 1.5]
    },
    "Textiles and Design": {
        "units": 2,
        "scale_factor": 0.93,
        "coefficients": [0.0, 0.92, 1.0]
    },
    # Add more subjects as needed
}
```

---

## 3. New Features to Build

### 3.1 Subject Management (`/subjects`)

**New template:** `subjects.html`

- List all subjects the student has added
- Each subject shows: name, units, current estimated mark, task count
- Buttons: Add Subject, Edit, Delete
- Clicking a subject name navigates to that subject's task/mark view

**New routes in `app.py`:**
```python
@app.route('/subjects')                        # List subjects
@app.route('/subjects/add', methods=['GET','POST'])   # Add subject
@app.route('/subjects/<int:subject_id>/edit')  # Edit subject
@app.route('/subjects/<int:subject_id>/delete', methods=['POST'])
```

---

### 3.2 Subject Tab Bar on Dashboard

On `index.html`, add a horizontal tab bar above the task list:

```
[ All Tasks ] [ Maths Adv ] [ English Adv ] [ Chemistry ] [ + Add Subject ]
```

Clicking a tab filters tasks to that subject only. Active tab styled with `--primary` underline.

Implement via URL parameter: `/?subject_id=3`

---

### 3.3 Assessment Marks Tracker (`/subjects/<id>/marks`)

**New template:** `marks.html`

- Table of all assessments for that subject
- Columns: Assessment Name | Weight (%) | Your Mark | Out Of | Weighted Score
- Running total at the bottom: "Current estimated mark: 74.3 / 100"
- Form to add a new assessment result
- Warning if total weights exceed 100%

**New routes:**
```python
@app.route('/subjects/<int:subject_id>/marks')
@app.route('/subjects/<int:subject_id>/marks/add', methods=['POST'])
@app.route('/subjects/<int:subject_id>/marks/<int:result_id>/delete', methods=['POST'])
```

---

### 3.4 ATAR Prediction Dashboard (`/atar`)

**New template:** `atar.html`

This is the ML feature — the centrepiece of the assessment.

**Page layout:**
1. Input section: for each subject, show current estimated mark (auto-filled from assessment results) with an editable field
2. "Predict My ATAR" button
3. Results section:
   - Table: Subject | Raw Mark | Scaled Mark | Contribution
   - Aggregate: Estimated ATAR (displayed prominently)
   - Chart: bar chart of raw vs scaled marks per subject (use Chart.js — already available)

**New route:**
```python
@app.route('/atar', methods=['GET', 'POST'])
```

---

## 4. Machine Learning Integration

### New file: `ml_model.py`

```python
"""
ATAR Prediction Module
======================
Uses Polynomial Regression (degree=2) to model the non-linear relationship
between a student's raw HSC marks and their scaled marks per subject.

Polynomial Regression chosen over Linear because UAC scaling curves are
demonstrably non-linear — high-scaling subjects compress marks differently
at the top end than the middle band.
"""

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from atar_scaling import SCALING_DATA


def get_scaled_mark(subject_name: str, raw_mark: float) -> float:
    """
    Apply polynomial regression to predict the scaled mark for a subject.
    
    Args:
        subject_name: Must match a key in SCALING_DATA
        raw_mark: Raw HSC mark (0-100)
    
    Returns:
        Predicted scaled mark (0-100, capped)
    """
    if subject_name not in SCALING_DATA:
        # Default: no scaling applied
        return raw_mark

    coeffs = SCALING_DATA[subject_name]["coefficients"]

    # Build training data from the polynomial coefficients
    # Generate synthetic (raw, scaled) pairs using the known curve
    raw_range = np.linspace(0, 100, 50).reshape(-1, 1)
    scaled_range = np.polyval(coeffs, raw_range.flatten()).reshape(-1, 1)
    scaled_range = np.clip(scaled_range, 0, 100)

    # Train Polynomial Regression (degree 2) pipeline
    model = make_pipeline(
        PolynomialFeatures(degree=2),
        LinearRegression()
    )
    model.fit(raw_range, scaled_range)

    # Predict scaled mark for the student's raw mark
    predicted = model.predict([[raw_mark]])[0][0]
    return float(np.clip(predicted, 0, 100))


def calculate_aggregate(subject_scaled_marks: list[dict]) -> float:
    """
    Calculate the HSC aggregate mark from scaled subject marks.

    NSW ATAR calculation:
    - Count best 10 units (English counts at least 2 units)
    - Aggregate = sum of scaled marks for best 10 units
    - ATAR derived from aggregate via UAC conversion table (approximated here)

    Args:
        subject_scaled_marks: List of dicts with keys 'scaled_mark' and 'units'

    Returns:
        Estimated ATAR (0.00 - 99.95)
    """
    # Sort by scaled mark descending
    sorted_subjects = sorted(
        subject_scaled_marks, key=lambda x: x['scaled_mark'], reverse=True
    )

    aggregate = 0.0
    units_counted = 0
    target_units = 10

    for subject in sorted_subjects:
        if units_counted >= target_units:
            break
        units_to_add = min(subject['units'], target_units - units_counted)
        aggregate += subject['scaled_mark'] * (units_to_add / subject['units'])
        units_counted += units_to_add

    # Approximate ATAR from aggregate (UAC conversion — linear approximation)
    # Aggregate range: ~0-500, ATAR range: 0-99.95
    atar = (aggregate / 500) * 99.95
    return round(min(atar, 99.95), 2)
```

### Dependencies to add to `requirements.txt`
```
Flask>=3.0.0
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
```

---

## 5. Security Patches (OWASP)

### Patch 1 — Weak Password Hashing (A02: Cryptographic Failures)

**Current issue:** `app.py` uses `hashlib.sha256` — not suitable for passwords (no salt, fast to brute-force).

**Fix:** Replace with `werkzeug.security`:

```python
# Remove this:
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()

# Replace with:
from werkzeug.security import generate_password_hash, check_password_hash
password_hash = generate_password_hash(password)

# And for login verification:
# Remove: hashlib.sha256(password.encode()).hexdigest() != user['password_hash']
# Replace:
if not check_password_hash(user['password_hash'], password):
    error = 'Incorrect password.'
```

### Patch 2 — Missing CSRF Protection (A01: Broken Access Control)

**Current issue:** All forms lack CSRF tokens — any site can submit forms on behalf of a logged-in user.

**Fix:** Install and configure Flask-WTF:

```
# requirements.txt
Flask-WTF>=1.2.0
```

```python
# app.py — in create_app()
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production')

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

```html
<!-- Add to every <form> in templates -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Patch 3 — Hardcoded Secret Key (A05: Security Misconfiguration)

**Current issue:** `SECRET_KEY='dev'` is hardcoded.

**Fix:**
```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-for-dev-only')
```

On PythonAnywhere, set `SECRET_KEY` as an environment variable in the WSGI config.

---

## 6. Code Quality Fixes

### Immediate fixes in `app.py`
- Remove the duplicate `date_filter` registration (appears twice — lines ~47 and ~75)
- Add module-level docstring explaining the app's purpose
- Add docstrings to every route function
- Ensure all route functions are PEP 8 compliant (max line length 79 chars)

### Remove unused files
- Delete `static/js/scripts.js` — references `flatpickr` which is never loaded, causes silent errors

### Add to `requirements.txt` comments
```
# Web framework
Flask>=3.0.0

# Security
Flask-WTF>=1.2.0

# Machine learning
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
```

---

## 7. GitHub Commit Strategy (15 minimum)

Suggested commit sequence:

```
1.  "Initial review: document Term 4 codebase structure"
2.  "SAST: Run Bandit scan — identified hardcoded secret key and SHA-256 hashing issues"
3.  "Security patch: replace hashlib.sha256 with werkzeug generate_password_hash"
4.  "Security patch: move SECRET_KEY to environment variable"
5.  "Security patch: install Flask-WTF and add CSRF tokens to all forms"
6.  "Refactor: remove duplicate date_filter registration in app.py"
7.  "Cleanup: delete unused static/js/scripts.js"
8.  "DB schema: add subjects and assessment_results tables"
9.  "Feature: add subject CRUD routes and subjects.html template"
10. "Feature: add assessment marks tracker routes and marks.html"
11. "Feature: update tasks table with subject_id foreign key"
12. "Feature: add subject tab bar to index.html dashboard"
13. "ML: create atar_scaling.py with UAC scaling data per subject"
14. "ML: implement ml_model.py — Polynomial Regression scaled mark prediction"
15. "Feature: add ATAR prediction dashboard route and atar.html template"
16. "UI: overhaul colour palette to navy/gold academic theme"
17. "UI: refactor base.html — remove gradients, add sidebar navigation"
18. "Deploy: update requirements.txt and test on PythonAnywhere"
19. "Docs: update README.md with security patch notes and ATAR feature guide"
20. "DAST: manual penetration test — verified CSRF and auth protections"
```

---

## 8. Navbar / Navigation Structure

Update the navbar in `base.html` to reflect the new structure:

```
[ HSC Planner ]   Dashboard   Subjects   ATAR Predictor   |   Welcome, [user]   Logout
```

On mobile: collapse into hamburger as before, but with the updated link set.

---

## 9. File Structure After Upgrade

```
Task_Organiser_App/
├── Task_Organiser/
│   ├── app.py                    # Updated routes + security patches
│   ├── db.py                     # Unchanged
│   ├── ml_model.py               # NEW — Polynomial Regression model
│   ├── atar_scaling.py           # NEW — UAC scaling data per subject
│   ├── task_schema.sql           # Updated — new tables added
│   ├── requirements.txt          # Updated — scikit-learn, Flask-WTF, numpy
│   ├── instance/
│   │   └── taskmanager.db
│   ├── static/
│   │   └── css/
│   │       └── styles.css        # Updated — new academic theme
│   └── templates/
│       ├── base.html             # Updated — navy theme, sidebar
│       ├── index.html            # Updated — subject tabs
│       ├── subjects.html         # NEW — subject list
│       ├── add_subject.html      # NEW — add/edit subject form
│       ├── marks.html            # NEW — assessment marks tracker
│       ├── atar.html             # NEW — ATAR prediction dashboard
│       ├── add_task.html         # Updated — subject dropdown replaces category
│       ├── edit_task.html        # Updated — subject dropdown
│       ├── login.html            # Updated — cleaner design
│       ├── register.html         # Updated — cleaner design
│       ├── about.html            # Minor update
│       └── contact.html          # Minor update
├── run.py                        # Unchanged
├── README.md                     # Updated
└── DEPLOY.md                     # Minor update for new env variable
```

---

## 10. Part A Documentation Checklist

When writing your Word document, use this as a checklist:

- [ ] **1.1** State: "Polynomial Regression (degree=2) was chosen because UAC subject scaling curves exhibit non-linear behaviour — marks in high-scaling subjects are compressed differently at the top band compared to mid-range, making a linear model insufficient."
- [ ] **1.2** Draw Level 0 DFD: Student → [HSC Planner System] → ATAR Prediction Output. Show security checkpoint (CSRF/auth) and ML component as a process bubble.
- [ ] **2.1** OWASP table: (1) SHA-256 password hashing → patched with werkzeug; (2) Missing CSRF → patched with Flask-WTF
- [ ] **2.2** SAST: Bandit scan on `app.py`. DAST: Manual form submission testing, auth bypass attempts.
- [ ] **3.1** 15+ commits (see Section 7)
- [ ] **3.2** Gantt chart covering 10 weeks: Weeks 1-2 security audit, 3-4 patching, 5-6 DB + subjects feature, 7-8 ML integration, 9 UI overhaul, 10 testing + deploy
- [ ] **4.1** Level 1 DFD: User → Login (auth check) → Dashboard → Subject data → ML Model → Scaled marks → ATAR output → User
- [ ] **5.1** Flowchart: Input raw marks → Apply polynomial coefficients → Predict scaled marks → Sort by units → Sum best 10 units → Convert aggregate to ATAR → Display
- [ ] **5.2** Updated DB schema diagram showing all 4 tables (users, subjects, tasks, assessment_results) with foreign key relationships
