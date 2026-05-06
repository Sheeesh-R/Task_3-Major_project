import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, current_app, session, g, jsonify
from .db import get_db, init_app
import hashlib
from functools import wraps


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'taskmanager.db'),
        SCHEMA_PATH='task_schema.sql'
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

    @app.template_filter('date_filter')
    def date_filter(value, format='%Y-%m-%d'):
        if value is None:
            return ''
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)

    @app.template_filter('truncate_title')
    def truncate_title(title):
        """Truncate title to first 3 words or 12 characters, whichever comes first"""
        if not title:
            return title
        
        # First try to get first 3 words
        words = title.split()
        if len(words) > 3:
            truncated = ' '.join(words[:3])
            # If 3 words are longer than 12 characters, truncate further
            if len(truncated) > 12:
                return truncated[:12] + '...'
            return truncated + '...'
        else:
            # If 3 or fewer words, check if any word is longer than 12 characters
            if len(title) > 12:
                return title[:12] + '...'
            return title

    return app


def register_routes(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
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
            elif not email:
                error = 'Email is required.'
            elif db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone() is not None:
                error = f'User {username} is already registered.'
            elif db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
                error = f'Email {email} is already registered.'

            if error is None:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                db.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                           (username, password_hash, email))
                db.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

            flash(error, 'error')

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            db = get_db()
            error = None
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif hashlib.sha256(password.encode()).hexdigest() != user['password_hash']:
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
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
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
            
            # Fetch assessment results for this subject (assignment tasks only)
            if current_subject:
                assessment_results = db.execute('''
                    SELECT ar.task_name, ar.weight, ar.raw_mark, ar.max_mark, ar.date_recorded
                    FROM assessment_results ar
                    JOIN tasks t ON ar.task_name = t.title
                    WHERE ar.subject_id = ? AND ar.user_id = ? AND t.category_id = (
                        SELECT id FROM categories WHERE name = 'Assignments'
                    )
                    ORDER BY ar.date_recorded ASC
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
        db = get_db()
        try:
            db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, g.user['id']))
            db.commit()
            flash('Task deleted successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error deleting task: {str(e)}', 'error')
        return redirect(url_for('index'))
        
    @app.route('/task/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def toggle_task_status(task_id):
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
                if 'task_count' not in subject_dict:
                    subject_dict['task_count'] = 0
                subjects_list.append(subject_dict)
            
            return render_template('subjects.html', subjects=subjects_list)
        except Exception as e:
            # If subjects table doesn't exist or has no data, return empty list
            return render_template('subjects.html', subjects=[])

    # Add subject route
    @app.route('/subjects/add', methods=['POST'])
    @login_required
    def add_subject():
        print("DEBUG: add_subject route reached")  # Debug print
        db = get_db()
        try:
            subject_name = request.form.get('subject_name')
            units = int(request.form.get('subject_units', 2))
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

    # Test route to verify routing works
    @app.route('/test')
    def test():
        return "Test route works!"

    # ATAR Predictor page
    @app.route('/atar', methods=['GET', 'POST'])
    @login_required
    def atar():
        if request.method == 'POST':
            # Handle ATAR prediction (placeholder for now)
            flash('ATAR prediction feature coming soon!', 'info')
            return redirect(url_for('atar'))
        
        # Sample data for demonstration
        sample_subjects = [
            {'name': 'Mathematics Advanced', 'raw_mark': 78, 'scaled_mark': 82, 'contribution': 16.4},
            {'name': 'English Advanced', 'raw_mark': 82, 'scaled_mark': 82, 'contribution': 16.4},
            {'name': 'Chemistry', 'raw_mark': 75, 'scaled_mark': 81, 'contribution': 16.2},
            {'name': 'Physics', 'raw_mark': 73, 'scaled_mark': 78, 'contribution': 15.6},
            {'name': 'Legal Studies', 'raw_mark': 80, 'scaled_mark': 76, 'contribution': 15.2}
        ]
        estimated_atar = 85.6  # Sample ATAR
        
        return render_template('atar.html', subjects=sample_subjects, estimated_atar=estimated_atar)

    # About page
    @app.route('/about')
    def about():
        return render_template('about.html')

    # Contact page
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
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


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
