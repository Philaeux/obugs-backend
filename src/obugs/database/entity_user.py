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
    roles = relationship("UserSoftwareRoleEntity", back_populates="user")

    def gql(self):
        software_is = {'mod': [], 'curator': [], 'editor': []}
        for role in self.roles:
            if role.role & 1 != 0:
                software_is['mod'].append(role.software_id)
            if role.role & 2 != 0:
                software_is['curator'].append(role.software_id)
            if role.role & 4 != 0:
                software_is['editor'].append(role.software_id)
        return User(
            id=self.id,
            username=self.username,
            is_admin=self.is_admin,
            is_banned=self.is_banned,
            software_is_mod=software_is['mod'],
            software_is_curator=software_is['curator'],
            software_is_editor=software_is['editor'],
        )
