from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from obugs.database.entity_base import BaseEntity
from obugs.graphql.types.software import Software


class SoftwareEntity(BaseEntity):
    __tablename__ = "software"

    id: Mapped[str] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    editor: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    tags: Mapped[List["TagEntity"]] = relationship(back_populates="software", cascade="all, delete-orphan")
    entries: Mapped[List["EntryEntity"]] = relationship(back_populates="software", cascade="all, delete-orphan")

    def gql(self):
        return Software(
            id=self.id,
            full_name=self.full_name,
            editor=self.editor,
            description=self.description
        )
