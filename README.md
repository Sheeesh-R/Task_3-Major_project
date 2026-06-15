# Task Organiser App

A Flask-based task management application designed to help students organize their workload efficiently. This application provides a clean, intuitive interface for managing tasks with due dates, priorities, and categories, now with user authentication for personalized task management and enhanced mobile responsiveness.

## Features

### Core Task Management
- **User Authentication**: Register, login, and logout functionality
- **Complete CRUD Operations**: Create, read, update, and delete tasks
- **Task Details**: Due dates, priorities (High/Medium/Low), and categories
- **Status Tracking**: Not Started, In Progress, Completed
- **Advanced Filtering**: Filter by status, priority, and category
- **Task Sorting**: Sort by due date, priority, or title
- **User Isolation**: Each user sees only their own tasks

### Enhanced User Interface
- **Mobile-First Design**: Fully responsive with optimized mobile experience
- **Overview Cards**: Visual task statistics with gradient styling
- **Academic Calendar**: Interactive calendar for date visualization
- **Task Actions**: Edit and delete buttons positioned next to task titles
- **Reload Functionality**: Quick page refresh button
- **Clean Design**: Removed decorative elements for modern appearance

### Mobile Responsiveness
- **Responsive Cards**: Properly sized overview cards on all screen sizes
- **Text Scaling**: Readable text sizes optimized for mobile devices
- **Touch-Friendly Buttons**: Appropriately sized action buttons for mobile interaction
- **Flexible Layout**: Adaptive layout for tablets and phones
- **Hidden Tasks Info**: Informative message about hidden completed tasks

### Technical Features
- **Sidebar Navigation**: Desktop sidebar with subject shortcuts and quick actions
- **Subject Editing**: Edit subject name, units, and target mark from the UI
- **AJAX Updates**: Real-time task status toggling without page reload
- **CSRF Protection**: Server-side and AJAX CSRF token handling via Flask-WTF
- **Database Optimization**: Added SQLite indexes and pagination for larger datasets
- **Dynamic Styling**: JavaScript-powered category colors and animations
- **Clean Code Architecture**: Separated concerns between templates and logic
- **Error Handling**: Robust error handling and user feedback

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
3. **Set up environment variables**

   Copy the example environment file and set a secure secret key:
   ```bash
   cp Task_Organiser_App/.env .env
   ```
   Edit `.env` and replace the `SECRET_KEY` value with your own random hex string. This key is used for signing session cookies and CSRF tokens. **Never commit your `.env` file to version control.**

   If no `SECRET_KEY` is set, the app falls back to an insecure default and logs a warning — this is only acceptable for local development.
4. **Run the development server**
   ```bash
   python run.py
   ```
5. Open your browser at http://127.0.0.1:5000 to view the application. You'll be redirected to login if not authenticated.

## Project Structure
```
Task_Organiser/
├── Task_Organiser/            # Main Flask application package
│   ├── app.py                 # Routes, filters, and app factory
│   ├── db.py                  # Database initialization and connection handling
│   ├── atar_data.py           # ATAR calculation logic
│   ├── task_schema.sql        # Database schema definitions
│   ├── schema_updates.sql     # Incremental schema migrations
│   └── templates/
│       ├── base.html          # Base template with common layout
│       ├── index.html         # Main dashboard with task list
│       ├── add_task.html      # Task creation form
│       ├── edit_task.html     # Task editing form
│       ├── login.html         # User login page
│       ├── register.html      # User registration page
│       ├── subjects.html      # Subject management page
│       ├── edit_subject.html  # Subject editing form
│       ├── atar.html          # ATAR calculator page
│       ├── atar_calculation.html  # ATAR explanation page
│       ├── about.html         # About page
│       ├── contact.html       # Contact form
│       ├── marks.html         # Marks tracking page
│       ├── 404.html           # Not found error page
│       └── 500.html           # Server error page
├── static/
│   └── css/
│       └── styles.css         # Custom CSS styles
├── tests/
│   └── test_atar_data.py      # ATAR calculation unit tests
├── instance/
│   └── taskmanager.db         # SQLite database (auto-created)
├── Task_Organiser_App/
│   └── .env                   # Environment variables (SECRET_KEY)
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
└── README.md
```

## Database Schema
The application uses SQLite with the following tables:
- **users**: User authentication and profile information
- **tasks**: Task details including status, priority, due dates, and subject assignment
- **subjects**: User-managed subjects with units and target marks
- **categories**: Task categorization system
- **assessment_results**: Assessment marks tracking with weighted calculations
- **atar_predictions**: Saved ATAR prediction results per user

The database is automatically initialized when the app starts if it doesn't exist. Schema migrations are applied incrementally.

## Mobile Features
The application includes extensive mobile optimizations:
- **Responsive Breakpoints**: Optimized for tablets (768px) and phones (576px)
- **Touch Optimization**: Larger touch targets and improved spacing
- **Performance**: Optimized JavaScript and CSS for mobile performance
- **Accessibility**: Semantic HTML and proper ARIA labels

## Recent Improvements
- Enhanced mobile responsiveness with proper text scaling
- Improved task action button placement and sizing
- Added reload functionality for quick page refresh
- Removed decorative elements for cleaner UI
- Fixed task toggle and delete functionality
- Improved error handling and user feedback
- Optimized calendar display on mobile devices

## Running Tests
The repository includes automated tests using `pytest`.

Run tests from the project root:
```bash
pytest tests/
```

Or using Python's built-in unittest discovery:
```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Contributing
When contributing to this project:
1. Follow the existing code style and structure
2. Test mobile responsiveness on different screen sizes
3. Ensure all functionality works on both desktop and mobile
4. Update documentation for any new features

## License
This project is provided as-is. Include your preferred license information here if you plan to publish or distribute the application.
