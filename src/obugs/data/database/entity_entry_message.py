from datetime import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger

from obugs.data.database.entity_base import BaseEntity


class EntryMessageEntity(BaseEntity):
    __tablename__ = "entry_message"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column()
    type: Mapped[str] = mapped_column()

    user: Mapped["UserEntity"] = relationship(back_populates="messages")
    entry: Mapped["EntryEntity"] = relationship(back_populates="messages")

    __mapper_args__ = {
        "polymorphic_identity": "entry_message",
        "polymorphic_on": "type",
    }

    def __init__(self, entry_id, user_id, type):
        super().__init__()
        self.entry_id = entry_id
        self.user_id = user_id
        self.type = type
        self.created_at = datetime.utcnow()


class EntryCommentEntity(EntryMessageEntity):
    comment: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "comment",
    }

    def __init__(self, entry_id, user_id, comment):
        super().__init__(entry_id, user_id, "comment")
        self.comment = comment


class EntryPetitionEntity(EntryMessageEntity):
    state_before: Mapped[str] = mapped_column(nullable=True)
    state_after: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[int] = mapped_column(BigInteger())
    rating_count: Mapped[int] = mapped_column(BigInteger())

    votes: Mapped[List["EntryPetitionVoteEntity"]] = relationship(
        back_populates="entry_petition", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "petition",
    }

    def __init__(self, entry_id, user_id, state_before, state_after):
        super().__init__(entry_id, user_id, "petition")
        self.state_before = state_before
        self.state_after = state_after
        self.rating = 0
        self.rating_count = 0
