from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from obugs.data.database.entity_base import BaseEntity, association_tags_entries


class TagEntity(BaseEntity):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"))

    software: Mapped["SoftwareEntity"] = relationship(back_populates="tags")
    entries: Mapped[List["EntryEntity"]] = relationship(secondary=association_tags_entries, back_populates="tags")

    def __init__(self, name, software_id):
        super().__init__()
        self.name = name
        self.software_id = software_id
