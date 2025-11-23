# Task Organiser App

A Flask-based task management application designed to help students organize their workload efficiently. This application provides a clean, intuitive interface for managing tasks with due dates, priorities, and categories, now with user authentication for personalized task management.

## Features
- **User Authentication**: Register, login, and logout functionality
- Create, read, update, and delete tasks with due dates and priorities
- Categorize tasks for better organization
- Track task status (Not Started, In Progress, Completed)
- Filter tasks by status, priority, and category
- User-specific task isolation (each user sees only their own tasks)
- Responsive design that works on desktop and mobile devices

## Requirements
- Python 3.10 or newer
- Virtual environment tool such as `venv` or `virtualenv`
- Flask and related dependencies (see requirements.txt)

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
3. **Run the development server**
   ```bash
   python run.py
   ```
4. Open your browser at http://127.0.0.1:5000 to view the application. You'll be redirected to login if not authenticated.

## Project Structure
```
Task_Organiser_App/Task_Organiser/
├── app.py
├── db.py
├── run.py
├── instance/
│   └── taskmanager.db
├── task_schema.sql
├── static/
│   └── ...
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add_task.html
│   ├── edit_task.html
│   ├── login.html
│   ├── register.html
│   └── ...
└── README.md
```

## Database Schema
The `task_schema.sql` file contains the table definitions required by the application, including users, tasks, and categories tables. The database is automatically initialized when the app starts if it doesn't exist.

## Running Tests
Currently, the project does not include automated tests. To contribute tests, consider using `pytest` with Flask's testing utilities.

## License
This project is provided as-is. Include your preferred license information here if you plan to publish or distribute the application.
