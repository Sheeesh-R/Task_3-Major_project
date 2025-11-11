# Recipe Manager Flask App

This project is a sample Flask-based CRUD application for managing recipes. It showcases a simple database-backed web app with templates and static assets packaged in a `flask-example/` directory structure.

## Features
- Create, read, update, and delete recipe entries stored in SQLite.
- Upload images for recipes, with automatic sanitisation and storage.
- Responsive frontend powered by Jinja2 templates and Bootstrap styles.
- Command-line helper to initialise the database schema.

## Requirements
- Python 3.10 or newer
- Virtual environment tool such as `venv`, `virtualenv`, or `conda`

## Getting Started
1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialise the SQLite database**
   ```bash
   flask --app app init-db
   ```
4. **Run the development server**
   ```bash
   flask --app app run --debug
   ```
5. Open your browser at http://127.0.0.1:5000 to view the application.

## Project Structure
```
flask-example/
├── app.py
├── db.py
├── instance/
│   └── recipes.db (created at runtime)
├── schema.sql
├── static/
│   └── ...
├── templates/
│   └── ...
└── README.md
```

## Database Schema
The `schema.sql` file contains the table definitions required by the application. Running `flask --app app init-db` executes this script to create the SQLite database in the `instance/` directory.

## Running Tests
Currently, the project does not include automated tests. To contribute tests, consider using `pytest` with Flask's testing utilities.

## License
This project is provided as-is. Include your preferred license information here if you plan to publish or distribute the application.
