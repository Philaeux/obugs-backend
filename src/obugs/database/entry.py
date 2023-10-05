from datetime import datetime
import enum
import uuid
from typing import List

import strawberry
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, Text, Index, event, UUID

from obugs.database.entity_base import Base
from obugs.database.entity_base import association_tags_entries


@strawberry.enum
class EntryStatus (enum.Enum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    WIP = "WIP"
    CHECK = "CHECK"
    FIXED = "FIXED"
    EXPECTED = "EXPECTED"
    DUPLICATE = "DUPLICATE"
    CLOSED = "CLOSED"


class Entry(Base):
    __tablename__ = "entry"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text())
    illustration: Mapped[str] = mapped_column(Text())
    status: Mapped[EntryStatus] = mapped_column()
    rating: Mapped[float] = mapped_column()
    rating_total: Mapped[int] = mapped_column(BigInteger(), default=2)
    rating_count: Mapped[int] = mapped_column(BigInteger(), default=1)
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    open_patches_count: Mapped[int] = mapped_column(default=0)

    software: Mapped["Software"] = relationship(back_populates="entries")
    tags: Mapped[List["Tag"]] = relationship(secondary=association_tags_entries)
    messages: Mapped[List["EntryMessage"]] = relationship(back_populates="entry", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_entry_software_and_update_at', software_id, updated_at.desc()),
    )


@event.listens_for(Entry.rating_total, 'set')
def on_rating_total_change(target, value, oldvalue, initiator):
    count = 1 if target.rating_count is None else target.rating_count
    target.rating = value / max(1, count)


@event.listens_for(Entry.rating_count, 'set')
def on_rating_count_change(target, value, oldvalue, initiator):
    total = 2 if target.rating_total is None else target.rating_total
    target.rating = total / max(1, value)
