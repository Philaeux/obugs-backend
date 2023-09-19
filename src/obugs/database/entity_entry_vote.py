from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Identity

from obugs.database.entity_base import BaseEntity
from obugs.graphql.types.entry_vote import EntryVote


class EntryVoteEntity(BaseEntity):
    __tablename__ = "entry_vote"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column()

    entry: Mapped["EntryEntity"] = relationship(back_populates="votes")
    user: Mapped["UserEntity"] = relationship(back_populates="votes")

    def gql(self):
        return EntryVote(
            id=self.id,
            entry_id=self.entry_id,
            user_id=self.user_id,
            rating=self.rating
        )
