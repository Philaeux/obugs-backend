from datetime import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, Index

from obugs.database.entity_base import BaseEntity
from obugs.graphql.types.entry_message import EntryMessage


class EntryMessageEntity(BaseEntity):
    __tablename__ = "entry_message"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("entry.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column()
    type: Mapped[str] = mapped_column()

    entry: Mapped["EntryEntity"] = relationship(back_populates="messages")
    user: Mapped["UserEntity"] = relationship(foreign_keys=[user_id])

    __table_args__ = (
        Index('idx_entry_message_entry_created_at', entry_id, created_at),
    )

    __mapper_args__ = {
        "polymorphic_identity": "entry_message",
        "polymorphic_on": "type",
    }

    def gql(self) -> EntryMessage:
        return EntryMessage(
            id=self.id,
            entry_id=self.entry_id,
            user_id=self.user_id,
            created_at=self.created_at,
            type=self.type,
            comment=None,
            state_before=None,
            state_after=None,
            rating_total=None,
            rating_count=None,
            is_closed=None,
            closed_by_id=None,
            closed_at=None,
            accepted=None
        )


class EntryMessageCreationEntity(EntryMessageEntity):
    state_after: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "creation",
    }

    def gql(self) -> EntryMessage:
        return EntryMessage(
            id=self.id,
            entry_id=self.entry_id,
            user_id=self.user_id,
            created_at=self.created_at,
            type=self.type,
            comment=None,
            state_before=None,
            state_after=self.state_after,
            rating_total=None,
            rating_count=None,
            is_closed=None,
            closed_by_id=None,
            closed_at=None,
            accepted=None
        )


class EntryMessageCommentEntity(EntryMessageEntity):
    comment: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "comment",
    }

    def gql(self) -> EntryMessage:
        return EntryMessage(
            id=self.id,
            entry_id=self.entry_id,
            user_id=self.user_id,
            created_at=self.created_at,
            type=self.type,
            comment=self.comment,
            state_before=None,
            state_after=None,
            rating_total=None,
            rating_count=None,
            is_closed=None,
            closed_by_id=None,
            closed_at=None,
            accepted=None
        )


class EntryMessagePatchEntity(EntryMessageEntity):
    state_before: Mapped[str] = mapped_column(nullable=True)
    state_after: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    rating_total: Mapped[int] = mapped_column(BigInteger(), nullable=True, default=1)
    rating_count: Mapped[int] = mapped_column(BigInteger(), nullable=True, default=1)
    is_closed: Mapped[bool] = mapped_column(nullable=True)
    closed_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=True)
    closed_at: Mapped[datetime] = mapped_column(nullable=True)
    accepted: Mapped[bool] = mapped_column(nullable=True)

    closed_by: Mapped["UserEntity"] = relationship(foreign_keys=[closed_by_id])

    __mapper_args__ = {
        "polymorphic_identity": "patch",
    }

    def gql(self) -> EntryMessage:
        return EntryMessage(
            id=self.id,
            entry_id=self.entry_id,
            user_id=self.user_id,
            created_at=self.created_at,
            type=self.type,
            comment=None,
            state_before=self.state_before,
            state_after=self.state_after,
            rating_total=self.rating_total,
            rating_count=self.rating_count,
            is_closed=self.is_closed,
            closed_by_id=self.closed_by_id,
            closed_at=self.closed_at,
            accepted=self.accepted
        )
