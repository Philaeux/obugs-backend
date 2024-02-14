import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, UUID

from obugs.database.base import Base


class Vote(Base):
    __tablename__ = "vote"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="votes")

    __table_args__ = (
        Index('idx_vote_user_subject', user_id, subject_id),
    )
