import os
import sqlite3

def init_db():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'recipes.db')
    
    # Create instance directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute the schema
    with open(os.path.join(os.path.dirname(__file__), 'rjsandbox1', 'schema.sql'), 'r') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {db_path}")

if __name__ == '__main__':
    init_db()
