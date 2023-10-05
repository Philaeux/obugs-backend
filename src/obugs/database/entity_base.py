import uuid

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Database model base class"""
    pass


association_tags_entries = Table(
    "association_tags_entries",
    Base.metadata,
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
    Column("entry_id", ForeignKey("entry.id"), primary_key=True),
)
