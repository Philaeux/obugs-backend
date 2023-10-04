import uuid
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index

from obugs.database.entity_base import BaseEntity, association_tags_entries
from obugs.graphql.types.tag import Tag


class TagEntity(BaseEntity):
    __tablename__ = "tag"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"), index=True)
    font_color: Mapped[str] = mapped_column()
    background_color: Mapped[str] = mapped_column()

    software: Mapped["SoftwareEntity"] = relationship(back_populates="tags")
    entries: Mapped[List["EntryEntity"]] = relationship(secondary=association_tags_entries, back_populates="tags")

    __table_args__ = (
        Index('idx_tag_software_id_name', software_id, name),
    )

    def gql(self):
        return Tag(
            id=self.id,
            name=self.name,
            software_id=self.software_id,
            font_color=self.font_color,
            background_color=self.background_color
        )
