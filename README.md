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
- **AJAX Updates**: Real-time task status toggling without page reload
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
3. **Run the development server**
   ```bash
   python run.py
   ```
4. Open your browser at http://127.0.0.1:5000 to view the application. You'll be redirected to login if not authenticated.

## Project Structure
```
Task_Organiser_App/Task_Organiser/
├── app.py                 # Main Flask application with routes and filters
├── db.py                  # Database initialization and connection handling
├── run.py                 # Application entry point
├── instance/
│   └── taskmanager.db     # SQLite database (auto-created)
├── task_schema.sql        # Database schema definitions
├── static/
│   └── css/              # Custom CSS files
├── templates/
│   ├── base.html         # Base template with common layout
│   ├── index.html        # Main dashboard with task list
│   ├── add_task.html     # Task creation form
│   ├── edit_task.html    # Task editing form
│   ├── login.html        # User login page
│   ├── register.html     # User registration page
│   └── ...
└── README.md
```

## Database Schema
The application uses SQLite with the following main tables:
- **users**: User authentication and profile information
- **tasks**: Task details including status, priority, due dates, and categories
- **categories**: Task categorization system

The database is automatically initialized when the app starts if it doesn't exist.

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
Currently, the project does not include automated tests. To contribute tests, consider using `pytest` with Flask's testing utilities.

## Contributing
When contributing to this project:
1. Follow the existing code style and structure
2. Test mobile responsiveness on different screen sizes
3. Ensure all functionality works on both desktop and mobile
4. Update documentation for any new features

## License
This project is provided as-is. Include your preferred license information here if you plan to publish or distribute the application.
