from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from obugs.utils.singleton_meta import SingletonMeta


class Database(metaclass=SingletonMeta):
    """Singleton defining database URI and unique resources.

    Attributes:
        uri: database location
        engine: database connection used for session generation
    """

    def __init__(self, uri: str = ""):
        """Defines all necessary resources (engine & session factory)"""
        dir_uri = Path(__file__).parent
        if uri == '':
            self.uri = f"sqlite+pysqlite:///{dir_uri}/sqlite.db"
        else:
            self.uri = uri
        self.engine = create_engine(self.uri, echo=False)
        self.session_factory = sessionmaker(self.engine)

    def check_migrations(self):
        """Apply database migrations if necessary"""
        dir_uri = Path(__file__).parent
        alembic = Path(dir_uri) / ".." / ".." / "alembic.ini"
        migrations = Path(dir_uri) / ".." / "alembic"
        alembic_cfg = Config(alembic)
        alembic_cfg.set_main_option('script_location', str(migrations))
        alembic_cfg.set_main_option('sqlalchemy.url', self.uri)
        command.upgrade(alembic_cfg, 'head')
