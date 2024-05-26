from pathlib import Path

import pytest
from starlette.testclient import TestClient

from obugs.backend import make_app
from obugs.settings import Settings


@pytest.fixture(scope="session")
def mock_app():
    sqlite_path = Path(__file__).parent / ".." / "sqlite.db"

    # Fresh Database
    if sqlite_path.exists():
        sqlite_path.unlink()
    settings = Settings()
    settings.database_uri = f"sqlite+pysqlite:///sqlite.db"
    settings.jwt_secret_key = "TEST_KEY"

    # Make app
    yield TestClient(make_app(settings))
