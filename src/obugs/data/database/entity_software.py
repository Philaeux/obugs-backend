from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.data.database.entity_base import BaseEntity


class SoftwareEntity(BaseEntity):
    __tablename__ = "software"

    id: Mapped[str] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    editor: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    tags: Mapped[List["TagEntity"]] = relationship(back_populates="software", cascade="all, delete-orphan")
    entries: Mapped[List["EntryEntity"]] = relationship(back_populates="software", cascade="all, delete-orphan")

    def __init__(self, software_id, full_name, editor, description):
        super().__init__()
        self.id = software_id
        self.full_name = full_name
        self.editor = editor
        self.description = description
