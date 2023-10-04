
import uuid
from typing import Annotated

import strawberry
from sqlalchemy import select, and_

from obugs.database.entry import Entry as EntryEntity, EntryStatus
from obugs.graphql.types import Entry


# noinspection PyArgumentList
@strawberry.type
class QueryEntry:

    @strawberry.field
    def entry(self, info, entry_id: uuid.UUID) -> Entry | None:
        with info.context['session_factory']() as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            return db_entry

    @strawberry.field
    def entries(self, info, software_id: str, status_filter: list[str] = ['CONFIRMED', 'WIP', 'CHECK'],
                order: str = '', limit: int = 20, offset: int = 0) -> list[Entry]:
        enum_filter = [EntryStatus[s] for s in status_filter if s in EntryStatus.__members__]
        if len(enum_filter) == 0:
            return []

        with info.context['session_factory']() as session:
            sql = select(EntryEntity) \
                .where(and_(EntryEntity.software_id == software_id, EntryEntity.status.in_(enum_filter)))

            if order == '' or order == 'updated':
                sql = sql.order_by(EntryEntity.updated_at.desc())
            elif order == 'rating':
                sql = sql.order_by(EntryEntity.rating.desc())
            sql = sql.offset(offset).limit(limit)

            return session.execute(sql).scalars().all()
