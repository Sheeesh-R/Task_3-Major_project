import logging
from app import create_app
from db import get_db

app = create_app()


def init_db() -> None:
    """Initialize the application's database using the bundled schema.

    This function is intended for one-off CLI usage during development.
    """
    logging.basicConfig(level=logging.INFO)
    with app.app_context():
        db = get_db()
        with app.open_resource('task_schema.sql', mode='r') as f:
            db.executescript(f.read())
        logging.getLogger(__name__).info('Database initialized successfully')


if __name__ == '__main__':
    init_db()
