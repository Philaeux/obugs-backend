from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Identity

from obugs.data.database.entity_base import BaseEntity


class EntryVoteEntity(BaseEntity):
    __tablename__ = "entry_vote"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column()

    entry: Mapped["EntryEntity"] = relationship(back_populates="votes")
    user: Mapped["UserEntity"] = relationship(back_populates="votes")
