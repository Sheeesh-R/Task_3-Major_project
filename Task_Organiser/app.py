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

    os.makedirs(app.instance_path, exist_ok=True)
    init_app(app)
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

        # Build query
        query = '''
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
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

        return render_template('index.html',
                             tasks=tasks,
                             categories=categories,
                             current_status=status or 'all',
                             current_priority=priority or 'all',
                             current_category=category_id or 'all')

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
            category_id = request.form.get('category_id')

            if not title:
                flash('Title is required', 'error')
            else:
                try:
                    # Convert empty string to None for due_date
                    due_date = due_date if due_date else None

                    db.execute(
                        'INSERT INTO tasks (title, description, due_date, priority, status, category_id, user_id) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (title, description, due_date, priority, status, category_id, g.user['id'])
                    )
                    db.commit()
                    flash('Task added successfully!', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    db.rollback()
                    flash(f'Error adding task: {str(e)}', 'error')

        categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
        return render_template('add_task.html', categories=categories)

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
            category_id = request.form.get('category_id')

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
                        'status = ?, category_id = ?, completed_at = ? WHERE id = ? AND user_id = ?',
                        (title, description, due_date, priority, status, category_id, completed_at, task_id, g.user['id'])
                    )
                    db.commit()
                    flash('Task updated successfully!', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    db.rollback()
                    flash(f'Error updating task: {str(e)}', 'error')

        categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
        return render_template('edit_task.html', task=dict(task), categories=categories)

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
