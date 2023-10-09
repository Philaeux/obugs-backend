import uuid

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import with_polymorphic

from obugs.database.entry_message import EntryMessage, EntryMessagePatch
from obugs.graphql.types import EntryMessagePatch as EntryMessagePatchGQL, \
    EntryMessageComment as EntryMessageCommentGQL, EntryMessageCreation as EntryMessageCreationQGL


@strawberry.type
class QueryEntryMessage:

    @strawberry.field
    def entry_messages(self, info, entry_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[EntryMessagePatchGQL | EntryMessageCommentGQL | EntryMessageCreationQGL]:
        with info.context['session_factory']() as session:
            sql = select(EntryMessage) \
                .where(EntryMessage.entry_id == entry_id) \
                .order_by(EntryMessage.created_at).offset(offset) \
                .limit(limit)
            db_messages = session.execute(sql).scalars().all()
            return db_messages

    @strawberry.field
    def open_patches(self, info, software_id: str | None) -> list[EntryMessagePatchGQL]:
        with info.context['session_factory']() as session:
            sql = select(EntryMessagePatch) \
                .where(EntryMessagePatch.is_closed == False)

            if software_id is not None:
                sql = sql.where(EntryMessagePatch.entry.software_id == software_id)

            sql = sql.order_by(EntryMessagePatch.created_at).limit(50)
            return session.execute(sql).scalars().all()
