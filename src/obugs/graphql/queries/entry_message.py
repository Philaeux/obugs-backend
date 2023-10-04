import uuid

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_entry_message import EntryMessageEntity, EntryMessagePatchEntity
from obugs.graphql.types.entry_message import EntryMessage


# noinspection PyArgumentList
@strawberry.type
class QueryEntryMessage:

    @strawberry.field
    def entry_messages(self, info, entry_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[EntryMessage]:
        with Session(info.context['engine']) as session:
            sql = select(EntryMessageEntity)\
                .where(EntryMessageEntity.entry_id == entry_id)\
                .order_by(EntryMessageEntity.created_at).offset(offset) \
                .limit(limit)
            db_messages = session.execute(sql).scalars().all()
            return [message.gql() for message in db_messages]

    @strawberry.field
    def patches(self, info, software_id: str | None) -> list[EntryMessage]:
        with Session(info.context['engine']) as session:
            sql = select(EntryMessagePatchEntity) \
                .where(EntryMessagePatchEntity.is_closed == False)

            if software_id is not None:
                sql = sql.where(EntryMessagePatchEntity.entry.software_id == software_id)

            sql = sql.order_by(EntryMessagePatchEntity.created_at).limit(50)
            db_messages = session.execute(sql).scalars().all()
            return [message.gql() for message in db_messages]
