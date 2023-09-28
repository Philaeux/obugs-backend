from typing import List
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.database.entity_base import BaseEntity
from obugs.graphql.types.user import User


class UserEntity(BaseEntity):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    is_admin: Mapped[bool] = mapped_column()
    is_banned: Mapped[bool] = mapped_column()
    
    is_activated: Mapped[bool] = mapped_column()
    activation_token: Mapped[str] = mapped_column(String(32))

    votes: Mapped[List["VoteEntity"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def gql(self):
        return User(
            id=self.id,
            username=self.username,
            is_admin=self.is_admin,
            is_banned=self.is_banned
        )
