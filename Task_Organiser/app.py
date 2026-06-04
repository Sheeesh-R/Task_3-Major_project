"""
HSC Study Planner - Flask Web Application
=======================================
A comprehensive task management and ATAR prediction system for HSC students.

This application allows students to:
- Track tasks by subject with priority and due dates
- Monitor assessment results and calculate estimated marks
- Predict ATAR scores using Polynomial Regression models
- Manage subjects and view academic progress

Features:
- Subject-based task organization
- Assessment marks tracking with weighted calculations
- ATAR prediction with UAC scaling data
- Academic-themed UI with navy/gold colour scheme
- Responsive design for desktop and mobile
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, current_app, session, g, jsonify
from .db import get_db, init_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Load environment variables from .env file
load_dotenv()


def login_required(view):
    """Decorator to require login for accessing a route."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'fallback-for-dev-only'),
        DATABASE=os.path.join(app.instance_path, 'taskmanager.db'),
        SCHEMA_PATH='task_schema.sql',
        WTF_CSRF_ENABLED=True
    )
    
    # Register custom Jinja2 filter HERE (inside create_app)
    @app.template_filter('date_filter')
    def date_filter(date_value):
        """Format a date for display"""
        if not date_value:
            return ''
        
        # If it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        
        # If it's a string, try to parse it
        try:
            date_obj = datetime.strptime(str(date_value), '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except:
            return str(date_value)
    
    os.makedirs(app.instance_path, exist_ok=True)
    init_app(app)
    # Enable CSRF protection for forms and state-changing requests
    csrf = CSRFProtect(app)
    
    # Database migration for subjects table
    with app.app_context():
        db = get_db()
        try:
            # Check if units column exists in subjects table
            cursor = db.execute("PRAGMA table_info(subjects)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'units' not in columns:
                db.execute('ALTER TABLE subjects ADD COLUMN units INTEGER NOT NULL DEFAULT 2')
                print("Added 'units' column to subjects table")
            
            if 'target_mark' not in columns:
                db.execute('ALTER TABLE subjects ADD COLUMN target_mark INTEGER')
                print("Added 'target_mark' column to subjects table")
                
            # Check if atar_predictions table exists
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='atar_predictions'")
            if cursor.fetchone() is None:
                # Create atar_predictions table
                db.execute('''
                    CREATE TABLE atar_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        atar_score REAL NOT NULL,
                        aggregate_score REAL NOT NULL,
                        prediction_date TEXT NOT NULL,
                        notes TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                print("Created 'atar_predictions' table")
                
            db.commit()
        except Exception as e:
            print(f"Migration error: {e}")
    
    register_routes(app)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    @app.template_filter('format_datetime')
    def format_datetime(value, format='%Y-%m-%d'):
        if value is None:
            return ''
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)

    @app.template_filter('priority_class')
    def priority_class(priority):
        classes = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'info'
        }
        return classes.get(priority, 'secondary')

    @app.template_filter('status_class')
    def status_class(status):
        classes = {
            'completed': 'success',
            'in_progress': 'primary',
            'not_started': 'secondary'
        }
        return classes.get(status, 'light')

    @app.template_filter('truncate_title')
    def truncate_title(title, max_chars=12):
        """Truncate title to first 3 words or max_chars characters, whichever comes first"""
        if not title:
            return title
        
        # First try to get first 3 words
        words = title.split()
        if len(words) > 3:
            truncated = ' '.join(words[:3])
            # If 3 words are longer than max_chars characters, truncate further
            if len(truncated) > max_chars:
                return truncated[:max_chars] + '...'
            return truncated + '...'
        else:
            # If 3 or fewer words, check if any word is longer than max_chars characters
            if len(title) > max_chars:
                return title[:max_chars] + '...'
            return title

    return app


def register_routes(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Handle user registration.
        
        GET: Display registration form
        POST: Process registration data and create new user
        """
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            email = request.form.get('email', '').strip()

            db = get_db()
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif len(password) < 8:
                error = 'Password must be at least 8 characters long.'
            elif not email:
                error = 'Email is required.'
            elif db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone() is not None:
                error = f'User {username} is already registered.'
            elif db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
                error = f'Email {email} is already registered.'

            if error is None:
                password_hash = generate_password_hash(password)
                db.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                           (username, password_hash, email))
                db.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

            flash(error, 'error')

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login.
        
        GET: Display login form
        POST: Authenticate user and create session
        """
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            db = get_db()
            error = None
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password_hash'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))

            flash(error, 'error')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        """Handle user logout by clearing session."""
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        """Display main dashboard with subject cards and task filters.
        
        Shows subject cards with progress, allows filtering by status,
        priority, category, and subject. Displays tasks and assessment results.
        """
        db = get_db()

        # Get filter parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        category_id = request.args.get('category')
        subject_id = request.args.get('subject_id')

        # Build query
        query = '''
            SELECT t.*, c.name as category_name, c.color as category_color, s.name as subject_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.user_id = ?
        '''
        params = [g.user['id']]

        if status and status != 'all':
            query += ' AND t.status = ?'
            params.append(status)

        if priority and priority != 'all':
            query += ' AND t.priority = ?'
            params.append(priority)

        if category_id and category_id != 'all':
            query += ' AND t.category_id = ?'
            params.append(category_id)

        if subject_id:
            query += ' AND t.subject_id = ?'
            params.append(subject_id)

        # Add sorting
        query += '''
            ORDER BY
                CASE WHEN t.due_date IS NULL THEN 1 ELSE 0 END,
                t.due_date ASC,
                CASE t.priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END
        '''

        tasks = db.execute(query, params).fetchall()
        categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
        
        # Get subjects data for dashboard
        try:
            subjects = db.execute('SELECT * FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
            subjects_list = [dict(subject) for subject in subjects] if subjects else []
            
            # Add task counts and progress for each subject
            for subject in subjects_list:
                # Count tasks for this subject
                task_count = db.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND subject_id = ?', 
                                      (g.user['id'], subject['id'])).fetchone()
                subject['task_count'] = task_count['count'] if task_count else 0
                
                # Count completed tasks
                completed_count = db.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND subject_id = ? AND status = "completed"', 
                                           (g.user['id'], subject['id'])).fetchone()
                completed = completed_count['count'] if completed_count else 0
                
                # Calculate progress
                if subject['task_count'] > 0:
                    subject['progress'] = int((completed / subject['task_count']) * 100)
                else:
                    subject['progress'] = 0
                    
                # Get highest priority task for this subject
                priority_task = db.execute('''
                    SELECT title, priority, due_date 
                    FROM tasks 
                    WHERE user_id = ? AND subject_id = ? AND status != "completed"
                    ORDER BY 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'medium' THEN 2 
                            WHEN 'low' THEN 3 
                            ELSE 4 
                        END,
                        due_date ASC
                    LIMIT 1
                ''', (g.user['id'], subject['id'])).fetchone()
                
                subject['priority_task'] = dict(priority_task) if priority_task else None
                subject['completed_tasks'] = completed
                
        except Exception as e:
            subjects_list = []

        # Get current subject info for header
        current_subject = None
        assessment_results = []
        if subject_id:
            current_subject = db.execute('SELECT * FROM subjects WHERE id = ? AND user_id = ?', 
                                        (subject_id, g.user['id'])).fetchone()
            
            # Fetch assessment results for this subject
            if current_subject:
                assessment_results = db.execute('''
                    SELECT task_name, weight, raw_mark, max_mark, date_recorded
                    FROM assessment_results 
                    WHERE subject_id = ? AND user_id = ? 
                    ORDER BY date_recorded ASC
                ''', (subject_id, g.user['id'])).fetchall()
                
                # Convert to list of dictionaries and calculate percentage
                assessment_results = [dict(result) for result in assessment_results]
                for i, result in enumerate(assessment_results):
                    result['percentage'] = round((result['raw_mark'] / result['max_mark']) * 100, 1) if result['max_mark'] > 0 else 0
                    result['test_number'] = i + 1

        return render_template('index.html',
                             tasks=tasks,
                             categories=categories,
                             subjects=subjects_list,
                             current_subject=current_subject,
                             assessment_results=assessment_results,
                             current_status=status or 'all',
                             current_priority=priority or 'all',
                             current_category=category_id or 'all',
                             subject_id=subject_id)

    @app.route('/task/add', methods=['GET', 'POST'])
    @login_required
    def add_task():
        """Handle adding new tasks.
        
        GET: Display add task form
        POST: Process form data and create new task
        """
        db = get_db()

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date = request.form.get('due_date')
            priority = request.form.get('priority', 'medium')
            status = request.form.get('status', 'not_started')
            subject_id = request.form.get('subject_id')

            if not title:
                flash('Title is required', 'error')
            else:
                try:
                    # Convert empty string to None for due_date
                    due_date = due_date if due_date else None

                    db.execute(
                        'INSERT INTO tasks (title, description, due_date, priority, status, subject_id, user_id) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (title, description, due_date, priority, status, subject_id, g.user['id'])
                    )
                    db.commit()
                    flash('Task added successfully!', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    db.rollback()
                    flash(f'Error adding task: {str(e)}', 'error')

        subjects = db.execute('SELECT * FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
        return render_template('add_task.html', subjects=subjects)

    @app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        """Handle editing existing tasks.
        
        GET: Display edit form with task data
        POST: Update task with new information
        """
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, g.user['id'])).fetchone()

        if task is None:
            flash('Task not found', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date = request.form.get('due_date')
            priority = request.form.get('priority', 'medium')
            status = request.form.get('status', 'not_started')
            subject_id = request.form.get('subject_id')

            if not title:
                flash('Title is required', 'error')
            else:
                try:
                    # Convert empty string to None for due_date
                    due_date = due_date if due_date else None

                    # Update completed_at timestamp if status changed to completed
                    completed_at = None
                    if status == 'completed' and task['status'] != 'completed':
                        completed_at = datetime.now().isoformat()

                    db.execute(
                        'UPDATE tasks SET title = ?, description = ?, due_date = ?, priority = ?, '
                        'status = ?, subject_id = ?, completed_at = ? WHERE id = ? AND user_id = ?',
                        (title, description, due_date, priority, status, subject_id, completed_at, task_id, g.user['id'])
                    )
                    db.commit()
                    flash('Task updated successfully!', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    db.rollback()
                    flash(f'Error updating task: {str(e)}', 'error')

        subjects = db.execute('SELECT * FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
        return render_template('edit_task.html', task=dict(task), subjects=subjects)

    @app.route('/task/<int:task_id>/delete', methods=['POST'])
    @login_required
    def delete_task(task_id):
        """Handle deletion of a specific task."""
        db = get_db()
        try:
            db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, g.user['id']))
            db.commit()
            flash('Task deleted successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error deleting task: {str(e)}', 'error')
        return redirect(url_for('index'))
        
    @app.route('/delete_completed_tasks', methods=['POST'])
    @login_required
    def delete_completed_tasks():
        """Handle bulk deletion of all completed tasks."""
        db = get_db()
        try:
            # Count completed tasks before deletion
            completed_count = db.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = ?', (g.user['id'], 'completed')).fetchone()[0]
            
            if completed_count > 0:
                db.execute('DELETE FROM tasks WHERE user_id = ? AND status = ?', (g.user['id'], 'completed'))
                db.commit()
                flash(f'Successfully deleted {completed_count} completed task(s)!', 'success')
            else:
                flash('No completed tasks to delete.', 'info')
        except Exception as e:
            db.rollback()
            flash(f'Error deleting completed tasks: {str(e)}', 'error')
        return redirect(url_for('index'))
        
    @app.route('/task/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def toggle_task_status(task_id):
        """Handle toggling task completion status."""
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, g.user['id'])).fetchone()

        if task is None:
            flash('Task not found', 'error')
            return redirect(url_for('index'))

        new_status = 'completed' if task['status'] != 'completed' else 'not_started'
        completed_at = datetime.now().isoformat() if new_status == 'completed' else None

        try:
            db.execute(
                'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ? AND user_id = ?',
                (new_status, completed_at, task_id, g.user['id'])
            )
            db.commit()
            flash(f'Task marked as {new_status.replace("_", " ").title()}!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error updating task status: {str(e)}', 'error')

        return redirect(url_for('index'))

    

    # Subjects page
    @app.route('/subjects')
    @login_required
    def subjects():
        """Display list of all subjects for the current user."""
        db = get_db()
        try:
            # Check if units column exists and select appropriate columns
            cursor = db.execute("PRAGMA table_info(subjects)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'units' in columns and 'target_mark' in columns:
                subjects = db.execute('SELECT * FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
            else:
                # Fallback for older schema
                subjects = db.execute('SELECT id, name, user_id FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
            
            # Convert to list of dictionaries and add default values for missing columns
            subjects_list = []
            for subject in subjects:
                subject_dict = dict(subject)
                if 'units' not in subject_dict:
                    subject_dict['units'] = 2
                if 'target_mark' not in subject_dict:
                    subject_dict['target_mark'] = None
                if 'estimated_mark' not in subject_dict:
                    subject_dict['estimated_mark'] = 0
                
                # Calculate estimated mark from assessment results
                assessment_results = db.execute('''
                    SELECT weight, raw_mark, max_mark 
                    FROM assessment_results 
                    WHERE subject_id = ? AND user_id = ?
                ''', (subject_dict['id'], g.user['id'])).fetchall()
                
                if assessment_results:
                    total_weighted_score = 0
                    total_weight = 0
                    for result in assessment_results:
                        percentage = (result['raw_mark'] / result['max_mark']) * 100 if result['max_mark'] > 0 else 0
                        weighted_score = percentage * (result['weight'] / 100)
                        total_weighted_score += weighted_score
                        total_weight += result['weight']
                    
                    subject_dict['estimated_mark'] = round(total_weighted_score, 1) if total_weight > 0 else 0
                else:
                    subject_dict['estimated_mark'] = 0
                
                # Calculate actual task count for this subject
                task_count = db.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND subject_id = ?', 
                                    (g.user['id'], subject_dict['id'])).fetchone()
                subject_dict['task_count'] = task_count['count'] if task_count else 0
                
                subjects_list.append(subject_dict)
            
            return render_template('subjects.html', subjects=subjects_list)
        except Exception as e:
            # If subjects table doesn't exist or has no data, return empty list
            return render_template('subjects.html', subjects=[])

    # Add subject route
    @app.route('/subjects/add', methods=['POST'])
    @login_required
    def add_subject():
        """Handle adding a new subject for the current user."""
        print("DEBUG: add_subject route reached")  # Debug print
        db = get_db()
        try:
            subject_data = request.form.get('subject_name')
            if subject_data and '|' in subject_data:
                subject_name, units = subject_data.split('|')
                units = int(units)
            else:
                subject_name = subject_data
                units = 2  # Default to 2 units if not specified
            target_mark = request.form.get('target_mark')
            
            print(f"DEBUG: subject_name={subject_name}, units={units}, target_mark={target_mark}")  # Debug print
            
            if subject_name:
                # Check if subject already exists for this user
                existing = db.execute(
                    'SELECT id FROM subjects WHERE user_id = ? AND name = ?',
                    (g.user['id'], subject_name)
                ).fetchone()
                
                if existing:
                    flash(f'Subject "{subject_name}" already exists!', 'error')
                    print("DEBUG: Subject already exists for this user")  # Debug print
                else:
                    cursor = db.execute(
                        'INSERT INTO subjects (user_id, name, units, target_mark) VALUES (?, ?, ?, ?)',
                        (g.user['id'], subject_name, units, target_mark)
                    )
                    db.commit()
                    flash(f'Subject "{subject_name}" added successfully!', 'success')
                    print("DEBUG: Subject added successfully")  # Debug print
            else:
                flash('Please select a subject name.', 'error')
                print("DEBUG: No subject name provided")  # Debug print
        except Exception as e:
            db.rollback()
            error_msg = str(e)
            if "UNIQUE constraint failed: subjects.name" in error_msg:
                flash(f'Subject "{subject_name}" already exists in the system. Please choose a different name or contact support.', 'error')
            else:
                flash(f'Error adding subject: {error_msg}', 'error')
            print(f"DEBUG: Error: {error_msg}")  # Debug print
        
        return redirect(url_for('subjects'))

    # Delete subject route
    @app.route('/subjects/<int:subject_id>/delete', methods=['POST'])
    @login_required
    def delete_subject(subject_id):
        """Handle deletion of a specific subject and its associated data."""
        db = get_db()
        try:
            # Check if subject exists and belongs to current user
            subject = db.execute('SELECT * FROM subjects WHERE id = ? AND user_id = ?', (subject_id, g.user['id'])).fetchone()
            
            if subject is None:
                flash('Subject not found', 'error')
                return redirect(url_for('subjects'))
            
            # Check if there are any tasks associated with this subject
            task_count = db.execute('SELECT COUNT(*) FROM tasks WHERE subject_id = ?', (subject_id,)).fetchone()[0]
            
            if task_count > 0:
                flash(f'Cannot delete subject "{subject["name"]}" because it has {task_count} associated task(s). Please delete or reassign the tasks first.', 'error')
                return redirect(url_for('subjects'))
            
            # Delete the subject
            db.execute('DELETE FROM subjects WHERE id = ? AND user_id = ?', (subject_id, g.user['id']))
            db.commit()
            flash(f'Subject "{subject["name"]}" deleted successfully!', 'success')
            
        except Exception as e:
            db.rollback()
            flash(f'Error deleting subject: {str(e)}', 'error')
        
        return redirect(url_for('subjects'))

    # Test route to verify routing works
    @app.route('/test')
    def test():
        """Simple test route to verify routing works."""
        return "Test route works!"

    # ATAR Predictor page
    @app.route('/atar', methods=['GET', 'POST'])
    @login_required
    def atar():
        """Handle ATAR prediction calculator.
        
        GET: Display ATAR calculator form
        POST: Calculate ATAR based on input marks and save results
        """
        from .atar_data import calculate_atar_estimate, SUBJECT_SCALING_POINTS
        
        db = get_db()
        
        if request.method == 'POST':
            try:
                # Get user's subjects from database
                user_subjects = db.execute('SELECT * FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
                
                if not user_subjects:
                    flash('Please add subjects first before calculating ATAR!', 'error')
                    return redirect(url_for('subjects'))
                
                # Collect marks for each subject
                subject_marks = []
                for subject in user_subjects:
                    mark_input = request.form.get(f'mark_{subject["id"]}')
                    if mark_input and mark_input.strip():
                        try:
                            mark = float(mark_input)
                            # Validate mark range based on subject type
                            if 'Extension' in subject['name'] and subject['name'] != 'Mathematics Extension 2':
                                # Most extensions are out of 50
                                if 0 <= mark <= 50:
                                    subject_marks.append({
                                        'subject_name': subject['name'],
                                        'hsc_mark': mark,
                                        'units': subject['units'] if 'units' in subject.keys() else 2
                                    })
                                else:
                                    flash(f'Invalid mark for {subject["name"]} (must be 0-50)', 'error')
                            else:
                                # Standard subjects are out of 100
                                if 0 <= mark <= 100:
                                    subject_marks.append({
                                        'subject_name': subject['name'],
                                        'hsc_mark': mark,
                                        'units': subject['units'] if 'units' in subject.keys() else 2
                                    })
                                else:
                                    flash(f'Invalid mark for {subject["name"]} (must be 0-100)', 'error')
                        except ValueError:
                            flash(f'Invalid mark for {subject["name"]}', 'error')
                            return redirect(url_for('atar'))
                
                # Debug: print what we collected
                print(f"DEBUG: subject_marks = {subject_marks}")
                
                if subject_marks:
                    try:
                        # Calculate ATAR using the new atar_data module
                        atar_result = calculate_atar_estimate(subject_marks)
                        print(f"DEBUG: atar_result = {atar_result}")
                        print(f"DEBUG: subject_results = {atar_result.get('subject_results', 'NOT FOUND')}")
                        
                        # Save prediction to database
                        db.execute('''INSERT INTO atar_predictions (user_id, prediction_date, aggregate_score, atar_score) VALUES (?, ?, ?, ?)''', (g.user['id'], datetime.now().isoformat(), atar_result['aggregate'], atar_result['atar']))
                        db.commit()
                        
                        flash(f'ATAR calculated: {atar_result["atar"]}', 'success')
                        return render_template('atar.html', 
                                     subjects=user_subjects, 
                                     estimated_atar=atar_result['atar'],
                                     user_subjects=user_subjects,
                                     atar_result=None)

                    except Exception as calc_error:
                        flash(f'Error in ATAR calculation: {str(calc_error)}', 'error')
                        db.rollback()
                else:
                    flash('Please enter at least one mark', 'error')
                    
            except Exception as e:
                flash(f'Error calculating ATAR: {str(e)}', 'error')
                db.rollback()
        
        # GET request - show form
        user_subjects = db.execute('SELECT * FROM subjects WHERE user_id = ? ORDER BY name', (g.user['id'],)).fetchall()
        
        # Get latest ATAR prediction if exists
        latest_prediction = db.execute('''SELECT * FROM atar_predictions WHERE user_id = ? ORDER BY prediction_date DESC LIMIT 1''', (g.user['id'],)).fetchone()
        
        estimated_atar = latest_prediction['atar_score'] if latest_prediction and latest_prediction['atar_score'] else 0
        
        return render_template('atar.html', 
                             estimated_atar=estimated_atar,
                             user_subjects=user_subjects,
                             available_subjects=list(SUBJECT_SCALING_POINTS.keys()))

    # ATAR Calculation Explanation page
    @app.route('/atar-calculation')
    @login_required
    def atar_calculation():
        """Explain how ATAR calculations work."""
        return render_template('atar_calculation.html')

    # About page
    @app.route('/about')
    def about():
        """Display about page with application information."""
        return render_template('about.html')

    # Contact page
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Handle contact form.
        
        GET: Display contact form
        POST: Process contact submission (currently shows success message)
        """
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            
            # Basic validation
            if not name or not email or not subject or not message:
                flash('All fields are required.', 'error')
            elif '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'error')
            else:
                # In a real application, you would send an email here
                # For now, we'll just show a success message
                flash('Thank you for your message! We\'ll get back to you soon.', 'success')
                return redirect(url_for('contact'))
        
        return render_template('contact.html')

    @app.route('/toggle_task/<int:task_id>', methods=['POST'])
    @login_required
    def toggle_task(task_id):
        """Handle AJAX task toggle for dynamic UI updates.
        
        Returns JSON response for frontend JavaScript handling.
        """
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, g.user['id'])).fetchone()
        
        if task is None:
            return jsonify({'success': False, 'error': 'Task not found'})
        
        try:
            data = request.get_json()
            completed = data.get('completed', False)
            
            new_status = 'completed' if completed else 'not_started'
            completed_at = datetime.now().isoformat() if completed else None
            
            db.execute(
                'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?',
                (new_status, completed_at, task_id)
            )
            db.commit()
            
            return jsonify({'success': True, 'status': new_status})
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'error': str(e)})

    # Assessment marks tracker routes
    @app.route('/subjects/<int:subject_id>/marks')
    @login_required
    def subject_marks(subject_id):
        """Display assessment marks for a specific subject.
        
        Shows all assessment results, calculates current estimated mark,
        and provides form to add new assessment results.
        """
        db = get_db()
        
        # Check if subject exists and belongs to current user
        subject = db.execute('SELECT * FROM subjects WHERE id = ? AND user_id = ?', 
                           (subject_id, g.user['id'])).fetchone()
        
        if subject is None:
            flash('Subject not found', 'error')
            return redirect(url_for('subjects'))
        
        # Get assessment results for this subject
        assessment_results = db.execute('''
            SELECT * FROM assessment_results 
            WHERE subject_id = ? AND user_id = ? 
            ORDER BY date_recorded ASC
        ''', (subject_id, g.user['id'])).fetchall()
        
        # Convert to list of dictionaries and calculate percentages
        results_list = []
        total_weighted_score = 0
        total_weight = 0
        
        for result in assessment_results:
            result_dict = dict(result)
            result_dict['percentage'] = round((result['raw_mark'] / result['max_mark']) * 100, 1) if result['max_mark'] > 0 else 0
            result_dict['weighted_score'] = round(result_dict['percentage'] * (result['weight'] / 100), 1)
            results_list.append(result_dict)
            total_weighted_score += result_dict['weighted_score']
            total_weight += result['weight']
        
        # Calculate current estimated mark
        current_mark = round(total_weighted_score, 1) if total_weight > 0 else 0
        
        return render_template('marks.html', 
                             subject=dict(subject),
                             assessment_results=results_list,
                             current_mark=current_mark,
                             total_weight=total_weight)

    @app.route('/subjects/<int:subject_id>/marks/add', methods=['POST'])
    @login_required
    def add_assessment_result(subject_id):
        """Add a new assessment result for a subject.
        
        Processes form data for assessment name, weight, marks,
        and validates input before saving to database.
        """
        db = get_db()
        
        # Check if subject exists and belongs to current user
        subject = db.execute('SELECT * FROM subjects WHERE id = ? AND user_id = ?', 
                           (subject_id, g.user['id'])).fetchone()
        
        if subject is None:
            flash('Subject not found', 'error')
            return redirect(url_for('subjects'))
        
        try:
            assessment_name = request.form.get('assessment_name', '').strip()
            weight = float(request.form.get('weight', 0))
            raw_mark = float(request.form.get('raw_mark', 0))
            max_mark = float(request.form.get('max_mark', 0))
            
            if not assessment_name:
                flash('Assessment name is required', 'error')
            elif weight <= 0 or weight > 100:
                flash('Weight must be between 0 and 100', 'error')
            elif raw_mark < 0 or max_mark <= 0:
                flash('Marks must be positive and max mark must be greater than 0', 'error')
            elif raw_mark > max_mark:
                flash('Raw mark cannot exceed maximum mark', 'error')
            else:
                db.execute('''
                    INSERT INTO assessment_results 
                    (subject_id, user_id, task_name, weight, raw_mark, max_mark, date_recorded)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (subject_id, g.user['id'], assessment_name, weight, raw_mark, max_mark, 
                      datetime.now().isoformat()))
                db.commit()
                flash('Assessment result added successfully!', 'success')
                
        except ValueError:
            flash('Invalid input values', 'error')
        except Exception as e:
            db.rollback()
            flash(f'Error adding assessment result: {str(e)}', 'error')
        
        return redirect(url_for('subject_marks', subject_id=subject_id))

    @app.route('/subjects/<int:subject_id>/marks/<int:result_id>/delete', methods=['POST'])
    @login_required
    def delete_assessment_result(subject_id, result_id):
        """Delete an assessment result.
        
        Removes specific assessment result and recalculates
        subject's estimated mark.
        """
        db = get_db()
        
        try:
            # Check if result exists and belongs to current user
            result = db.execute('''
                SELECT ar.* FROM assessment_results ar
                JOIN subjects s ON ar.subject_id = s.id
                WHERE ar.id = ? AND ar.subject_id = ? AND ar.user_id = ? AND s.user_id = ?
            ''', (result_id, subject_id, g.user['id'], g.user['id'])).fetchone()
            
            if result is None:
                flash('Assessment result not found', 'error')
            else:
                db.execute('DELETE FROM assessment_results WHERE id = ?', (result_id,))
                db.commit()
                flash('Assessment result deleted successfully!', 'success')
                
        except Exception as e:
            db.rollback()
            flash(f'Error deleting assessment result: {str(e)}', 'error')
        
        return redirect(url_for('subject_marks', subject_id=subject_id))


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
