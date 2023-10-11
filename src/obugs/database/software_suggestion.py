import uuid

from obugs.database.entity_base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, Text


class SoftwareSuggestion(Base):
    __tablename__ = "software_suggestion"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text())
