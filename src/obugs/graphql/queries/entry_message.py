import uuid

from sqlalchemy import select
from strawberry.types import Info

from obugs.database.entry_message import EntryMessage, EntryMessagePatch
from obugs.graphql.types.generated import EntryMessagePatch as EntryMessagePatchGQL, \
    EntryMessageComment as EntryMessageCommentGQL, EntryMessageCreation as EntryMessageCreationQGL


async def entry_messages(info: Info, entry_id: uuid.UUID, limit: int = 50, offset: int = 0) \
        -> list[EntryMessagePatchGQL | EntryMessageCommentGQL | EntryMessageCreationQGL]:
    with info.context['session_factory']() as session:
        sql = select(EntryMessage) \
            .where(EntryMessage.entry_id == entry_id) \
            .order_by(EntryMessage.created_at).offset(offset) \
            .limit(limit)
        db_messages = session.execute(sql).scalars().all()
        return db_messages


async def entry_messages_open_patches(info: Info, software_id: str | None) -> list[EntryMessagePatchGQL]:
    with info.context['session_factory']() as session:
        sql = select(EntryMessagePatch) \
            .where(EntryMessagePatch.is_closed == False)

        if software_id is not None:
            sql = sql.join(EntryMessagePatch.entry).filter_by(software_id=software_id)

        sql = sql.order_by(EntryMessagePatch.created_at.desc()).limit(50)
        return session.execute(sql).scalars().all()
