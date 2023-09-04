from datetime import datetime
import enum
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, Text

from obugs.data.database.entity_base import BaseEntity, association_tags_entries


class EntryStatus (enum.Enum):
    NEW = "NEW"
    OPEN = "OPEN"
    FIXED = "FIXED"
    CLOSED = "CLOSED"


class EntryEntity(BaseEntity):
    __tablename__ = "entry"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text())
    status: Mapped[EntryStatus] = mapped_column()
    rating_total: Mapped[int] = mapped_column(BigInteger())
    rating_count: Mapped[int] = mapped_column(BigInteger())
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

    software: Mapped["SoftwareEntity"] = relationship(back_populates="entries")
    tags: Mapped[List["TagEntity"]] = relationship(secondary=association_tags_entries, back_populates="entries")
    messages: Mapped[List["EntryMessageEntity"]] = relationship(back_populates="entry", cascade="all, delete-orphan")
    votes: Mapped[List["EntryVoteEntity"]] = relationship(back_populates="entry", cascade="all, delete-orphan")

    def __init__(self, software_id, title, description):
        super().__init__()
        self.software_id = software_id
        self.title = title
        self.description = description
        self.status = EntryStatus.NEW
        self.rating_total = 2
        self.rating_count = 1
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
