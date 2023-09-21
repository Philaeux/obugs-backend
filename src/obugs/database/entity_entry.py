from datetime import datetime
import enum
import json
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, Text, Identity

from obugs.database.entity_base import BaseEntity, association_tags_entries
from obugs.graphql.types.entry import Entry


class EntryStatus (enum.Enum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    WIP = "WIP"
    CHECK = "CHECK"
    FIXED = "FIXED"
    EXPECTED = "EXPECTED"
    DUPLICATE = "DUPLICATE"
    CLOSED = "CLOSED"


class EntryEntity(BaseEntity):
    __tablename__ = "entry"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text())
    illustration: Mapped[str] = mapped_column(Text())
    status: Mapped[EntryStatus] = mapped_column()
    rating_total: Mapped[int] = mapped_column(BigInteger(), default=2)
    rating_count: Mapped[int] = mapped_column(BigInteger(), default=1)
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

    software: Mapped["SoftwareEntity"] = relationship(back_populates="entries")
    tags: Mapped[List["TagEntity"]] = relationship(secondary=association_tags_entries, back_populates="entries")
    messages: Mapped[List["EntryMessageEntity"]] = relationship(back_populates="entry", cascade="all, delete-orphan")
    votes: Mapped[List["EntryVoteEntity"]] = relationship(back_populates="entry", cascade="all, delete-orphan")

    def gql(self) -> Entry:
        return Entry(
            id=self.id,
            software_id=self.software_id,
            title=self.title,
            tags=[tag.gql() for tag in self.tags],
            description=self.description,
            illustration=self.illustration,
            created_at=self.created_at,
            updated_at=self.updated_at,
            status=self.status.name,
            rating_total=self.rating_total,
            rating_count=self.rating_count
        )

    def export_snapshot(self):
        return json.dumps({
            'title': self.title,
            'description': self.description,
            'illustration': self.illustration,
            'status': str(self.status.value),
            'tags': [str(tag.name) for tag in self.tags]
        })