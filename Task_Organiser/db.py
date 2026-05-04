import os
import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        database_path = current_app.config['DATABASE']
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_path = os.path.join(current_app.root_path, current_app.config.get('SCHEMA_PATH', 'task_schema.sql'))
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())


def update_db_schema():
    """Apply database schema updates for HSC Study Planner"""
    db = get_db()
    
    # Check if subjects table exists
    try:
        db.execute('SELECT 1 FROM subjects LIMIT 1')
        subjects_exists = True
    except sqlite3.OperationalError:
        subjects_exists = False
    
    # Check if assessment_results table exists
    try:
        db.execute('SELECT 1 FROM assessment_results LIMIT 1')
        assessment_results_exists = True
    except sqlite3.OperationalError:
        assessment_results_exists = False
    
    # Check if tasks table has subject_id column
    try:
        db.execute('SELECT subject_id FROM tasks LIMIT 1')
        subject_id_exists = True
    except sqlite3.OperationalError:
        subject_id_exists = False
    
    # Apply schema updates if needed
    if not subjects_exists or not assessment_results_exists or not subject_id_exists:
        schema_updates_path = os.path.join(current_app.root_path, 'schema_updates.sql')
        if os.path.exists(schema_updates_path):
            with open(schema_updates_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            click.echo('Database schema updated.')
        else:
            click.echo('Schema updates file not found.')
    else:
        click.echo('Database schema is up to date.')


def init_app(app):
    app.teardown_appcontext(close_db)
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    
    # Initialize the database if it doesn't exist
    with app.app_context():
        db = get_db()
        try:
            # Try to query the users table to see if it exists
            db.execute('SELECT 1 FROM users LIMIT 1')
            # Database exists, check for schema updates
            update_db_schema()
        except sqlite3.OperationalError:
            # If the query fails, initialize the database
            init_db()
            click.echo('Initialized the database.')
            # Apply schema updates after initialization
            update_db_schema()

    @app.cli.command('init-db')
    def init_db_command():
        """Clear existing data and create new tables."""
        init_db()
        click.echo('Initialized the database.')
    
    @app.cli.command('update-db')
    def update_db_command():
        """Update database schema without clearing data."""
        update_db_schema()


__all__ = ['get_db', 'init_db', 'update_db_schema', 'init_app']
