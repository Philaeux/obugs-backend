import strawberry
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
import uuid

from obugs.database.database import Database
from obugs.database.entity_entry import EntryEntity, EntryStatus
from obugs.graphql.types.entry import Entry


# noinspection PyArgumentList
@strawberry.type
class QueryEntry:

    @strawberry.field
    def entry(self, info, entry_id: uuid.UUID) -> Entry | None:
        with Session(info.context['engine']) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return None
            else:
                return db_entry.gql()

    @strawberry.field
    def entries(self, info, software_id: str, status_filter: list[str] = ['CONFIRMED', 'WIP', 'CHECK'],
                limit: int = 20, offset: int = 0) -> list[Entry]:
        enum_filter = [EntryStatus[s] for s in status_filter if s in EntryStatus.__members__]
        if len(enum_filter) == 0:
            return []

        with Session(info.context['engine']) as session:
            sql = select(EntryEntity) \
                .where(and_(EntryEntity.software_id == software_id, EntryEntity.status.in_(enum_filter))) \
                .order_by(EntryEntity.updated_at.desc()).offset(offset) \
                .limit(limit)

            db_entries = session.execute(sql).scalars().all()
            return [entry.gql() for entry in db_entries]
