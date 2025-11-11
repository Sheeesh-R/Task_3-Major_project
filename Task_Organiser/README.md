# Task Organiser App

A Flask-based task management application designed to help students organize their workload efficiently. This application provides a clean, intuitive interface for managing tasks with due dates, priorities, and categories.

## Features
- Create, read, update, and delete tasks with due dates and priorities
- Categorize tasks for better organization
- Track task status (Not Started, In Progress, Completed)
- Interactive calendar view to visualize due dates
- Filter tasks by status, priority, and category
- Responsive design that works on desktop and mobile devices

## Requirements
- Python 3.10 or newer
- Virtual environment tool such as `venv` or `virtualenv`

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
