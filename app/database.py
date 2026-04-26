from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

Base = declarative_base()

engine = None
SessionLocal = None
configured_database_url = None
INCIDENT_TABLE_COLUMNS = {
    "id",
    "source_event_id",
    "event_type",
    "severity",
    "status",
    "description",
    "confidence",
    "camera_id",
    "highway_id",
    "road_marker",
    "lane_no",
    "latitude",
    "longitude",
    "image_url",
    "detected_at",
    "ingested_at",
    "status_note",
    "extra_payload",
    "updated_at",
}


def configure_database(force: bool = False) -> None:
    global engine, SessionLocal, configured_database_url

    settings = get_settings()
    database_url = settings.database_url

    if not force and engine is not None and configured_database_url == database_url:
        return

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    configured_database_url = database_url


def get_engine():
    configure_database()
    return engine


def init_db() -> None:
    configure_database()
    import app.models.incident  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_incident_events()


def _migrate_sqlite_incident_events() -> None:
    settings = get_settings()
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "incident_events" not in inspector.get_table_names():
        return

    current_column_definitions = {column["name"]: column for column in inspector.get_columns("incident_events")}
    current_columns = set(current_column_definitions)
    has_all_columns = INCIDENT_TABLE_COLUMNS.issubset(current_columns)
    allows_optional_coordinates = all(
        current_column_definitions.get(column_name, {}).get("nullable", False)
        for column_name in ("latitude", "longitude")
    )
    if has_all_columns and allows_optional_coordinates:
        return

    with engine.begin() as connection:
        rows = connection.execute(text("SELECT * FROM incident_events")).mappings().all()
        connection.execute(text("DROP TABLE incident_events"))

    Base.metadata.create_all(bind=engine)

    if not rows:
        return

    insert_sql = text(
        """
        INSERT INTO incident_events (
            id, source_event_id, event_type, severity, status, description, confidence,
            camera_id, highway_id, road_marker, lane_no, latitude, longitude, image_url,
            detected_at, ingested_at, status_note, extra_payload, updated_at
        ) VALUES (
            :id, :source_event_id, :event_type, :severity, :status, :description, :confidence,
            :camera_id, :highway_id, :road_marker, :lane_no, :latitude, :longitude, :image_url,
            :detected_at, :ingested_at, :status_note, :extra_payload, :updated_at
        )
        """
    )

    with engine.begin() as connection:
        for row in rows:
            payload = dict(row)
            payload.setdefault("source_event_id", payload["id"])
            payload.setdefault("road_marker", None)
            payload.setdefault("lane_no", None)
            payload.setdefault("latitude", None)
            payload.setdefault("longitude", None)
            payload.setdefault("status_note", None)
            payload.setdefault("extra_payload", None)
            connection.execute(insert_sql, payload)


def get_db() -> Generator[Session, None, None]:
    configure_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
