import os
import sqlite3
import logging

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection for the current application context."""
    if "db" not in g:
        database_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e: Exception | None = None) -> None:
    """Close and remove the database connection from the application context."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> None:
    """Initialize the database using the bundled schema file."""
    db = get_db()
    schema_path = os.path.join(
        current_app.root_path, current_app.config.get("SCHEMA_PATH", "task_schema.sql")
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())


def update_db_schema() -> None:
    """Apply database schema updates for HSC Study Planner.

    This will run optional schema migration scripts and create helpful
    indexes if they are missing.
    """
    db = get_db()

    def has_index(name):
        return (
            db.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name = ?",
                (name,),
            ).fetchone()
            is not None
        )

    def create_index(name: str, sql: str) -> None:
        try:
            if not has_index(name):
                db.execute(sql)
        except sqlite3.OperationalError as e:
            logging.getLogger(__name__).warning(
                "Failed to create index %s: %s", name, e
            )

    # Check if subjects table exists
    try:
        db.execute("SELECT 1 FROM subjects LIMIT 1")
        subjects_exists = True
    except sqlite3.OperationalError:
        subjects_exists = False

    # Check if assessment_results table exists
    try:
        db.execute("SELECT 1 FROM assessment_results LIMIT 1")
        assessment_results_exists = True
    except sqlite3.OperationalError:
        assessment_results_exists = False

    # Check if tasks table exists
    try:
        db.execute("SELECT 1 FROM tasks LIMIT 1")
        tasks_exists = True
    except sqlite3.OperationalError:
        tasks_exists = False

    # Check if tasks table has subject_id column
    try:
        db.execute("SELECT subject_id FROM tasks LIMIT 1")
        subject_id_exists = True
    except sqlite3.OperationalError:
        subject_id_exists = False

    # Apply schema updates if needed
    if not subjects_exists or not assessment_results_exists or not subject_id_exists:
        schema_updates_path = os.path.join(current_app.root_path, "schema_updates.sql")
        if os.path.exists(schema_updates_path):
            with open(schema_updates_path, "r", encoding="utf-8") as f:
                db.executescript(f.read())
            db.commit()
            click.echo("Database schema updated.")
        else:
            logging.getLogger(__name__).warning(
                "Schema updates file not found at %s", schema_updates_path
            )
    else:
        click.echo("Database schema is up to date.")

    if tasks_exists:
        create_index(
            "idx_tasks_user_id", "CREATE INDEX idx_tasks_user_id ON tasks (user_id)"
        )
        create_index(
            "idx_tasks_subject_id",
            "CREATE INDEX idx_tasks_subject_id ON tasks (subject_id)",
        )
        create_index(
            "idx_tasks_status", "CREATE INDEX idx_tasks_status ON tasks (status)"
        )
        create_index(
            "idx_tasks_priority", "CREATE INDEX idx_tasks_priority ON tasks (priority)"
        )

    if subjects_exists:
        create_index(
            "idx_subjects_user_id",
            "CREATE INDEX idx_subjects_user_id ON subjects (user_id)",
        )

    if assessment_results_exists:
        create_index(
            "idx_assessment_results_subject_user",
            "CREATE INDEX idx_assessment_results_subject_user ON assessment_results (subject_id, user_id)",
        )

    if tasks_exists or subjects_exists or assessment_results_exists:
        db.commit()


def init_app(app) -> None:
    """Register database handlers and CLI commands on the Flask app.

    Args:
        app: Flask application instance.
    """
    app.teardown_appcontext(close_db)

    # Ensure the database directory exists
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    # Initialize the database if it doesn't exist
    with app.app_context():
        db = get_db()
        try:
            # Try to query the users table to see if it exists
            db.execute("SELECT 1 FROM users LIMIT 1")
            # Database exists, check for schema updates
            update_db_schema()
        except sqlite3.OperationalError:
            # If the query fails, initialize the database
            init_db()
            logging.getLogger(__name__).info("Initialized the database.")
            # Apply schema updates after initialization
            update_db_schema()

    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        init_db()
        logging.getLogger(__name__).info("Initialized the database.")

    @app.cli.command("update-db")
    def update_db_command():
        """Update database schema without clearing data."""
        update_db_schema()


__all__ = ["get_db", "init_db", "update_db_schema", "init_app"]
