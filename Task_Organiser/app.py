import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from db import get_db, init_app


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
    @app.route('/')
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
            WHERE 1=1
        '''
        params = []
        
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
                        'INSERT INTO tasks (title, description, due_date, priority, status, category_id) '
                        'VALUES (?, ?, ?, ?, ?, ?)',
                        (title, description, due_date, priority, status, category_id)
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
    def edit_task(task_id):
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        
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
                        'status = ?, category_id = ?, completed_at = ? WHERE id = ?',
                        (title, description, due_date, priority, status, category_id, completed_at, task_id)
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
    def delete_task(task_id):
        db = get_db()
        try:
            db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            db.commit()
            flash('Task deleted successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error deleting task: {str(e)}', 'error')
        return redirect(url_for('index'))
        
    @app.route('/task/<int:task_id>/toggle', methods=['POST'])
    def toggle_task_status(task_id):
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        
        if task is None:
            flash('Task not found', 'error')
            return redirect(url_for('index'))
            
        new_status = 'completed' if task['status'] != 'completed' else 'not_started'
        completed_at = datetime.now().isoformat() if new_status == 'completed' else None
        
        try:
            db.execute(
                'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?',
                (new_status, completed_at, task_id)
            )
            db.commit()
            flash(f'Task marked as {new_status.replace("_", " ").title()}!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error updating task status: {str(e)}', 'error')
            
        return redirect(url_for('index'))

    # Simple about page
    @app.route('/about')
    def about():
        return "<h1>About Student Task Manager</h1><p>A simple task management application for students to organize their workload.</p>"

    # Simple contact page
    @app.route('/contact')
    def contact():
        return "<h1>Contact</h1><p>For support, please contact the application administrator.</p>"


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
