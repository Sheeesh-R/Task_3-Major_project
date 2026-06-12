"""Database connection, initialisation and schema migration.

This module manages the SQLite database lifecycle:

- ``get_db()`` returns a per-request connection (closed automatically).
- ``init_db()`` creates tables from ``task_schema.sql``.
- ``update_db_schema()`` applies incremental migrations and creates
  performance indexes on frequently queried columns.

Security notes
--------------
- All queries in the application use parameterised placeholders (``?``)
  to prevent SQL injection.
- The database file is stored in ``instance/taskmanager.db`` (outside the
  application package) so it is never served to users.
"""

import os
import sqlite3
import logging

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection scoped to the current request.

    Connections are stored on Flask's ``g`` object and automatically
    closed by ``close_db`` when the request ends.
    """
    if "db" not in g:
        database_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e: Exception | None = None) -> None:
    """Close the database connection stored on ``g``."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create all tables from ``task_schema.sql`` (destructive)."""
    db = get_db()
    schema_path = os.path.join(
        current_app.root_path,
        current_app.config.get("SCHEMA_PATH", "task_schema.sql"),
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())


def update_db_schema() -> None:
    """Apply incremental schema migrations and create performance indexes.

    Safe to run repeatedly -- missing tables/columns are added, existing
    ones are left untouched.  Indexes are only created if they do not
    already exist.
    """
    db = get_db()

    def has_index(name: str) -> bool:
        return (
            db.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name = ?",
                (name,),
            ).fetchone()
            is not None
        )

    def create_index(name: str, sql: str) -> None:
        """Create an index only if it does not already exist."""
        try:
            if not has_index(name):
                db.execute(sql)
        except sqlite3.OperationalError as e:
            logging.getLogger(__name__).warning(
                "Failed to create index %s: %s", name, e
            )

    # --- Check which tables exist -----------------------------------------
    def table_exists(table_name: str) -> bool:
        """Check if a table exists using sqlite_master (no user input)."""
        result = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        return result is not None

    subjects_exists = table_exists("subjects")
    assessment_results_exists = table_exists("assessment_results")
    tasks_exists = table_exists("tasks")
    subject_id_exists = False
    if tasks_exists:
        try:
            db.execute("SELECT subject_id FROM tasks LIMIT 1")
            subject_id_exists = True
        except sqlite3.OperationalError:
            pass

    # --- Apply schema migrations if needed --------------------------------
    if not subjects_exists or not assessment_results_exists or not subject_id_exists:
        schema_updates_path = os.path.join(
            current_app.root_path, "schema_updates.sql"
        )
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

    # --- Create performance indexes ---------------------------------------
    # Indexes speed up the most common queries (user_id lookups, status
    # filtering, subject grouping).
    if tasks_exists:
        create_index(
            "idx_tasks_user_id",
            "CREATE INDEX idx_tasks_user_id ON tasks (user_id)",
        )
        create_index(
            "idx_tasks_subject_id",
            "CREATE INDEX idx_tasks_subject_id ON tasks (subject_id)",
        )
        create_index(
            "idx_tasks_status",
            "CREATE INDEX idx_tasks_status ON tasks (status)",
        )
        create_index(
            "idx_tasks_priority",
            "CREATE INDEX idx_tasks_priority ON tasks (priority)",
        )

    if subjects_exists:
        create_index(
            "idx_subjects_user_id",
            "CREATE INDEX idx_subjects_user_id ON subjects (user_id)",
        )

    if assessment_results_exists:
        create_index(
            "idx_assessment_results_subject_user",
            "CREATE INDEX idx_assessment_results_subject_user "
            "ON assessment_results (subject_id, user_id)",
        )

    if tasks_exists or subjects_exists or assessment_results_exists:
        db.commit()


def init_app(app) -> None:
    """Register database teardown and CLI commands on the Flask app.

    Also ensures the database directory exists and the schema is current.
    """
    app.teardown_appcontext(close_db)

    # Ensure the database directory exists before connecting.
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    # Auto-initialise the database on first run.
    with app.app_context():
        db = get_db()
        try:
            db.execute("SELECT 1 FROM users LIMIT 1")
            # Database exists -- apply any pending migrations.
            update_db_schema()
        except sqlite3.OperationalError:
            # Fresh install -- create tables, then apply migrations.
            init_db()
            logging.getLogger(__name__).info("Initialized the database.")
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
