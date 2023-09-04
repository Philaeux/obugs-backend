from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger

from obugs.data.database.entity_base import BaseEntity


class EntryPetitionVoteEntity(BaseEntity):
    __tablename__ = "entry_petition_vote"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    entry_petition_id: Mapped[int] = mapped_column(ForeignKey("entry_message.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column()

    entry_petition: Mapped["EntryPetitionEntity"] = relationship(back_populates="votes")
    user: Mapped["UserEntity"] = relationship(back_populates="petition_votes")

    def __init__(self, entry_message_id, user_id, rating):
        super().__init__()
        self.entry_message_id = entry_message_id
        self.user_id = user_id
        self.rating = rating
