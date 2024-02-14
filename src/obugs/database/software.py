from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.database.base import Base


class Software(Base):
    __tablename__ = "software"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column()
    editor: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column()

    tags: Mapped[List["Tag"]] = relationship(back_populates="software", cascade="all, delete-orphan")
    entries: Mapped[List["Entry"]] = relationship(back_populates="software", cascade="all, delete-orphan")
    user_roles = relationship("UserSoftwareRole", back_populates="software", cascade="all, delete-orphan")
