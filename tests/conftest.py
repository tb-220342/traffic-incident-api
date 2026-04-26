import sys
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest_asyncio.fixture
async def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_incidents.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.database import Base, configure_database, get_engine, init_db
    from app.main import create_app

    configure_database(force=True)
    Base.metadata.drop_all(bind=get_engine())
    init_db()

    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client

    with get_engine().connect() as connection:
        connection.execute(text("DELETE FROM incident_events"))
        connection.commit()
