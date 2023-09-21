from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Identity

from obugs.database.entity_base import BaseEntity


class EntryPetitionVoteEntity(BaseEntity):
    __tablename__ = "entry_petition_vote"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    entry_petition_id: Mapped[int] = mapped_column(ForeignKey("entry_message.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column(default=1)

    entry_petition: Mapped["EntryMessagePetitionEntity"] = relationship(back_populates="votes")
    user: Mapped["UserEntity"] = relationship(back_populates="petition_votes")
