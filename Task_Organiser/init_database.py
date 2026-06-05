import os
import sqlite3
import logging
from app import create_app


def init_db() -> None:
    """Create a fresh database by applying the bundled schema.

    This removes any existing database file and re-initializes it.
    """
    logging.basicConfig(level=logging.INFO)
    # Create the Flask app
    app = create_app()
    
    # Get the database path from the app config
    db_path = app.config['DATABASE']
    schema_path = os.path.join(app.root_path, 'task_schema.sql')
    
    # Ensure the instance folder exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Delete the existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create a new database and initialize it with the schema
    with app.app_context():
        # Read the schema file
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Connect to the database and execute the schema
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        
        logging.getLogger(__name__).info('Database initialized successfully at %s', db_path)


if __name__ == '__main__':
    init_db()
