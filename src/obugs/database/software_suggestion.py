import uuid

from obugs.database.entity_base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, Text, ForeignKey


class SoftwareSuggestion(Base):
    __tablename__ = "software_suggestion"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("user.id"))
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
