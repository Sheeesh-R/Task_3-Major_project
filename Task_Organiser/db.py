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
        except sqlite3.OperationalError:
            # If the query fails, initialize the database
            init_db()
            click.echo('Initialized the database.')

    @app.cli.command('init-db')
    def init_db_command():
        """Clear existing data and create new tables."""
        init_db()
        click.echo('Initialized the database.')


__all__ = ['get_db', 'init_db', 'init_app']
