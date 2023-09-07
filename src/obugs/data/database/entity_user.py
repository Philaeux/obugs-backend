from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.data.database.entity_base import BaseEntity


class UserEntity(BaseEntity):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    is_activated: Mapped[bool] = mapped_column()
    activation_token: Mapped[str] = mapped_column(String(32))

    messages: Mapped[List["EntryMessageEntity"]] = relationship(back_populates="user")
    votes: Mapped[List["EntryVoteEntity"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    petition_votes: Mapped[List["EntryPetitionVoteEntity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")

    def __init__(self, username, password, email, activation_token):
        super().__init__()
        self.username = username
        self.password = password
        self.email = email
        self.is_activated = False
        self.activation_token = activation_token
