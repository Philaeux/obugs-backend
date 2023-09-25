import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from sqlalchemy import create_engine

from obugs.database.entity_base import BaseEntity, association_tags_entries
from obugs.database.entity_software import SoftwareEntity
from obugs.database.entity_user import UserEntity
from obugs.database.entity_tag import TagEntity
from obugs.database.entity_entry import EntryEntity, EntryStatus
from obugs.database.entity_vote import VoteEntity
from obugs.database.entity_entry_message import (EntryMessageCommentEntity, EntryMessageEntity,
                                                 EntryMessagePatchEntity, EntryMessageCreationEntity)


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
        alembic = Path(dir_uri) / ".." / ".." / "alembic.ini"
        migrations = Path(dir_uri) / ".." / "alembic"
        if uri == '':
            self.uri = f"sqlite+pysqlite:///{dir_uri}/sqlite.db"
        else:
            self.uri = uri
        self.engine = create_engine(self.uri, echo=False)

        # Upgrade application to heads
        if check_migrations:
            alembic_cfg = Config(alembic)
            alembic_cfg.set_main_option('script_location', str(migrations))
            alembic_cfg.set_main_option('sqlalchemy.url', self.uri)
            command.upgrade(alembic_cfg, 'head')
