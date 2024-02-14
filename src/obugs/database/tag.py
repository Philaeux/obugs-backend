import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, UUID

from obugs.database.base import Base


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    software_id: Mapped[str] = mapped_column(ForeignKey("software.id"), index=True)
    font_color: Mapped[str] = mapped_column()
    background_color: Mapped[str] = mapped_column()

    software: Mapped["Software"] = relationship("Software", foreign_keys=software_id, back_populates="tags")

    __table_args__ = (
        Index('idx_tag_software_id_name', software_id, name),
    )
