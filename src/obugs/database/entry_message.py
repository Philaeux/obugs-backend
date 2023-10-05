from datetime import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, Index, UUID

from obugs.database.entity_base import Base


class EntryMessage(Base):
    __tablename__ = "entry_message"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    entry_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("entry.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column()
    type: Mapped[str] = mapped_column()

    entry: Mapped["Entry"] = relationship(back_populates="messages")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    __table_args__ = (
        Index('idx_entry_message_entry_created_at', entry_id, created_at),
    )

    __mapper_args__ = {
        "polymorphic_identity": "entry_message",
        "polymorphic_on": "type",
    }


class EntryMessageCreation(EntryMessage):
    state_after: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)

    __mapper_args__ = {
        "polymorphic_identity": "creation",
        "polymorphic_load": "inline",
    }


class EntryMessageComment(EntryMessage):
    comment: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "comment",
        "polymorphic_load": "inline",
    }


class EntryMessagePatch(EntryMessage):
    state_before: Mapped[str] = mapped_column(nullable=True)
    state_after: Mapped[str] = mapped_column(nullable=True, use_existing_column=True)
    rating_total: Mapped[int] = mapped_column(BigInteger(), nullable=True, default=1)
    rating_count: Mapped[int] = mapped_column(BigInteger(), nullable=True, default=1)
    is_closed: Mapped[bool] = mapped_column(nullable=True)
    closed_by_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("user.id"), nullable=True)
    closed_at: Mapped[datetime] = mapped_column(nullable=True)
    accepted: Mapped[bool] = mapped_column(nullable=True)

    closed_by: Mapped["User"] = relationship(foreign_keys=[closed_by_id])

    __mapper_args__ = {
        "polymorphic_identity": "patch",
        "polymorphic_load": "inline",
    }

