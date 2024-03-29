import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from obugs.database.base import Base
from obugs.database.software import Software
from obugs.database.user import User
from obugs.database.tag import Tag
from obugs.database.entry import Entry, EntryStatus
from obugs.database.user_software_role import UserSoftwareRole
from obugs.database.vote import Vote
from obugs.database.entry_message import (EntryMessageComment, EntryMessage,
                                          EntryMessagePatch, EntryMessageCreation)
from obugs.database.software_suggestion import SoftwareSuggestion


class Database:
    """Singleton defining database URI and unique ressources.

    Attributes:
        _instance: Singleton instance
        uri: database location
        engine: database connection used for session generation
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """New overload to create a singleton."""
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, uri='', check_migrations=False):
        """Defines all necessary ressources (URI & engine) and create database if necessary."""

        dir_uri = os.path.dirname(__file__)
        if uri == '':
            self.uri = f"sqlite+pysqlite:///{dir_uri}/sqlite.db"
        else:
            self.uri = uri
        self.engine = create_engine(self.uri, echo=False)
        self.session_factory = sessionmaker(self.engine)

        # Upgrade application to heads
        if check_migrations:
            alembic = Path(dir_uri) / ".." / ".." / "alembic.ini"
            migrations = Path(dir_uri) / ".." / "alembic"
            alembic_cfg = Config(alembic)
            alembic_cfg.set_main_option('script_location', str(migrations))
            alembic_cfg.set_main_option('sqlalchemy.url', self.uri)
            command.upgrade(alembic_cfg, 'head')
