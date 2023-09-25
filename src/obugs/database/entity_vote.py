import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from obugs.database.entity_base import BaseEntity
from obugs.graphql.types.vote import Vote


class VoteEntity(BaseEntity):
    __tablename__ = "vote"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column()

    user: Mapped["UserEntity"] = relationship(back_populates="votes")

    def gql(self):
        return Vote(
            id=self.id,
            subject_id=self.subject_id,
            user_id=self.user_id,
            rating=self.rating
        )
