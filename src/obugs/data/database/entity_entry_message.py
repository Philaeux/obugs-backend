from datetime import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, Identity

from obugs.data.database.entity_base import BaseEntity


class EntryMessageEntity(BaseEntity):
    __tablename__ = "entry_message"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    type: Mapped[str] = mapped_column()

    user: Mapped["UserEntity"] = relationship(back_populates="messages")
    entry: Mapped["EntryEntity"] = relationship(back_populates="messages")

    __mapper_args__ = {
        "polymorphic_identity": "entry_message",
        "polymorphic_on": "type",
    }


class EntryMessageCreationEntity(EntryMessageEntity):
    state_after: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "creation",
    }


class EntryMessageCommentEntity(EntryMessageEntity):
    comment: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "comment",
    }


class EntryMessagePetitionEntity(EntryMessageEntity):
    state_before: Mapped[str] = mapped_column(nullable=True)
    state_after: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    rating: Mapped[int] = mapped_column(BigInteger(), nullable=True)
    rating_count: Mapped[int] = mapped_column(BigInteger(), nullable=True)

    votes: Mapped[List["EntryPetitionVoteEntity"]] = relationship(
        back_populates="entry_petition", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "petition",
    }
