from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class BaseEntity(DeclarativeBase):
    """Database model base class"""
    pass


association_tags_entries = Table(
    "association_tags_entries",
    BaseEntity.metadata,
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
    Column("entry_id", ForeignKey("entry.id"), primary_key=True),
)
