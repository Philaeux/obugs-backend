from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Identity

from obugs.data.database.entity_base import BaseEntity, association_tags_entries


class TagEntity(BaseEntity):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column()
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"))
    font_color: Mapped[str] = mapped_column()
    background_color: Mapped[str] = mapped_column()

    software: Mapped["SoftwareEntity"] = relationship(back_populates="tags")
    entries: Mapped[List["EntryEntity"]] = relationship(secondary=association_tags_entries, back_populates="tags")

    def __init__(self, name, software_id, font_color='#000000', background_color='#e0e0e0'):
        super().__init__()
        self.name = name
        self.software_id = software_id
