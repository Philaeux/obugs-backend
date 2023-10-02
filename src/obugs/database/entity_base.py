from uuid import UUID
from sqlalchemy import Table, Column, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class BaseEntity(DeclarativeBase):
    """Database model base class"""
    pass


association_tags_entries = Table(
    "association_tags_entries",
    BaseEntity.metadata,
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
    Column("entry_id", ForeignKey("entry.id"), primary_key=True),
)


class UserSoftwareRoleEntity(BaseEntity):
    __tablename__ = "user_software_role"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    software_id: Mapped[UUID] = mapped_column(ForeignKey("software.id"), primary_key=True)
    role: Mapped[int] = mapped_column(default=0)
    # 1: mod, 2: curator, 4: editor

    software: Mapped["SoftwareEntity"] = relationship(back_populates="user_roles")
    user: Mapped["UserEntity"] = relationship(back_populates="roles")
