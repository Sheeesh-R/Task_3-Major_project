from rjsandbox1.app import create_app
from rjsandbox1.db import init_db, get_db

app = create_app()
with app.app_context():
    init_db()
    print("Database initialized successfully!")
