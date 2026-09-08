from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


def _normalize_database_url(url: str) -> str:
    """Accept mysql://… and rewrite to mysql+pymysql:// for SQLAlchemy."""
    url = url.strip()
    if url.startswith("mysql://"):
        return "mysql+pymysql://" + url[len("mysql://") :]
    if url.startswith("mariadb://"):
        return "mysql+pymysql://" + url[len("mariadb://") :]
    return url


def _default_sqlite_url() -> str:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'survey.db'}"


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", "").strip() or _default_sqlite_url()
)

_engine_kwargs: dict = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)


@event.listens_for(engine, "connect")
def _on_connect(dbapi_connection, _connection_record):
    if engine.dialect.name == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def _table_names(conn) -> set[str]:
    dialect = engine.dialect.name
    if dialect == "sqlite":
        rows = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()
        return {row[0] for row in rows}
    if dialect == "mysql":
        rows = conn.execute(text("SHOW TABLES")).fetchall()
        return {row[0] for row in rows}
    return set()


def _column_names(conn, table: str) -> set[str]:
    dialect = engine.dialect.name
    if dialect == "sqlite":
        rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
        return {row[1] for row in rows}
    if dialect == "mysql":
        rows = conn.execute(text(f"SHOW COLUMNS FROM `{table}`")).fetchall()
        return {row[0] for row in rows}
    return set()


def ensure_schema() -> None:
    """Add columns introduced after initial create_all (SQLite + MySQL)."""
    with engine.begin() as conn:
        tables = _table_names(conn)
        if "responses" in tables:
            cols = _column_names(conn, "responses")
            if "status" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE responses ADD COLUMN status VARCHAR(32) DEFAULT 'complete'"
                    )
                )
                conn.execute(
                    text("UPDATE responses SET status = 'complete' WHERE status IS NULL")
                )
            if "edit_token" not in cols:
                conn.execute(
                    text("ALTER TABLE responses ADD COLUMN edit_token VARCHAR(64) NULL")
                )
        if "surveys" in tables:
            survey_cols = _column_names(conn, "surveys")
            if "language" not in survey_cols:
                conn.execute(
                    text(
                        "ALTER TABLE surveys ADD COLUMN language VARCHAR(8) DEFAULT 'en'"
                    )
                )
                conn.execute(
                    text("UPDATE surveys SET language = 'en' WHERE language IS NULL")
                )
        if "users" in tables:
            user_cols = _column_names(conn, "users")
            if "is_superadmin" not in user_cols:
                default_false = "0" if engine.dialect.name == "sqlite" else "0"
                conn.execute(
                    text(
                        f"ALTER TABLE users ADD COLUMN is_superadmin BOOLEAN DEFAULT {default_false}"
                    )
                )
                conn.execute(
                    text(
                        "UPDATE users SET is_superadmin = 0 WHERE is_superadmin IS NULL"
                    )
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_host_hint() -> str:
    """Safe host label for logs (no credentials)."""
    try:
        parsed = urlparse(DATABASE_URL)
        return parsed.hostname or "unknown"
    except Exception:
        return "unknown"
