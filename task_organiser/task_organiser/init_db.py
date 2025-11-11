from app import create_app
from db import get_db

app = create_app()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('task_schema.sql', mode='r') as f:
            db.executescript(f.read())
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
