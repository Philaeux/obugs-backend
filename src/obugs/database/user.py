from typing import List
import uuid

from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.database.entity_base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4, index=True)

    github_id: Mapped[int] = mapped_column(nullable=True, index=True)
    github_name: Mapped[str] = mapped_column(nullable=True)
    reddit_id: Mapped[str] = mapped_column(nullable=True, index=True)
    reddit_name: Mapped[str] = mapped_column(nullable=True)

    is_admin: Mapped[bool] = mapped_column()
    is_banned: Mapped[bool] = mapped_column()

    username: Mapped[str] = mapped_column()

    votes: Mapped[List["Vote"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["UserSoftwareRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def is_role_on_software(self, target_role, software_id):
        for role in self.roles:
            if role.software_id == software_id and role.role & target_role != 0:
                return True
        return False
