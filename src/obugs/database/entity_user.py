from typing import List

from sqlalchemy import String, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.database.entity_base import BaseEntity
from obugs.graphql.types.user import User


class UserEntity(BaseEntity):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    is_activated: Mapped[bool] = mapped_column(default=False)
    activation_token: Mapped[str] = mapped_column(String(32))

    messages: Mapped[List["EntryMessageEntity"]] = relationship(back_populates="user")
    votes: Mapped[List["EntryVoteEntity"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    petition_votes: Mapped[List["EntryPetitionVoteEntity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")

    def gql(self):
        return User(
            id=self.id,
            username=self.username
        )
