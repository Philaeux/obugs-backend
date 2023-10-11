import uuid
from enum import IntFlag

from sqlalchemy import ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.database.entity_base import Base


class SoftwareRole(IntFlag):
    MOD = 1
    CURATOR = 2
    EDITOR = 4


class UserSoftwareRole(Base):
    __tablename__ = "user_software_role"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("user.id"), primary_key=True)
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"), primary_key=True)
    role: Mapped[int] = mapped_column(default=0)

    software: Mapped["Software"] = relationship(back_populates="user_roles")
    user: Mapped["User"] = relationship(back_populates="roles")
