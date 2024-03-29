import asyncio
import uuid

from sqlalchemy import select, and_
from strawberry.types import Info

from obugs.database.entry import Entry, EntryStatus
from obugs.graphql.types.generated import Entry as EntryGQL


async def entry(info: Info, entry_id: uuid.UUID) -> EntryGQL | None:
    with info.context['session_factory']() as session:
        db_entry = session.query(Entry).where(Entry.id == entry_id).one_or_none()
        len(db_entry.tags)
        return db_entry


async def entries(info: Info, software_id: str, search_filter: str | None,
                  status_filter: list[str] = ['CONFIRMED', 'WIP', 'CHECK'], order: str = '', limit: int = 20,
                  offset: int = 0) -> list[EntryGQL]:
    asyncio.get_event_loop()
    enum_filter = [EntryStatus[s] for s in status_filter if s in EntryStatus.__members__]
    if len(enum_filter) == 0:
        return []

    with info.context['session_factory']() as session:
        sql = select(Entry) \
            .where(and_(Entry.software_id == software_id, Entry.status.in_(enum_filter)))

        if search_filter is not None:
            sql = sql.filter(Entry.title.ilike(f"%{search_filter}%"))
        if order == '' or order == 'updated':
            sql = sql.order_by(Entry.updated_at.desc())
        elif order == 'rating':
            sql = sql.order_by(Entry.rating.desc())
        sql = sql.offset(offset).limit(limit)

        db_entries = session.execute(sql).scalars().all()
        for entry in db_entries:
            len(entry.tags)
        return db_entries
