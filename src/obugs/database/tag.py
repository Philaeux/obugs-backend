

import uuid
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, UUID

from obugs.database.entity_base import Base, association_tags_entries


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"), index=True)
    font_color: Mapped[str] = mapped_column()
    background_color: Mapped[str] = mapped_column()

    software: Mapped["Software"] = relationship("Software", foreign_keys=software_id, back_populates="tags")
    entries: Mapped[List["Entry"]] = relationship(secondary=association_tags_entries, back_populates="tags")

    __table_args__ = (
        Index('idx_tag_software_id_name', software_id, name),
    )
