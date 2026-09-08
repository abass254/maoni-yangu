from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'survey.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_schema() -> None:
    """Add columns introduced after initial create_all (SQLite-safe)."""
    with engine.begin() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
        }
        if "responses" in tables:
            cols = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(responses)")).fetchall()
            }
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
                    text("ALTER TABLE responses ADD COLUMN edit_token VARCHAR(64)")
                )
        if "surveys" in tables:
            survey_cols = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(surveys)")).fetchall()
            }
            if "language" not in survey_cols:
                conn.execute(
                    text("ALTER TABLE surveys ADD COLUMN language VARCHAR(8) DEFAULT 'en'")
                )
                conn.execute(
                    text("UPDATE surveys SET language = 'en' WHERE language IS NULL")
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
