import uuid

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_entry_message import EntryMessageEntity
from obugs.graphql.types.entry_message import EntryMessage


# noinspection PyArgumentList
@strawberry.type
class QueryEntryMessage:

    @strawberry.field
    def entry_messages(self, entry_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[EntryMessage]:
        with Session(Database().engine) as session:
            sql = select(EntryMessageEntity)\
                .where(EntryMessageEntity.entry_id == entry_id)\
                .order_by(EntryMessageEntity.created_at).offset(offset) \
                .limit(limit)
            db_messages = session.execute(sql).scalars().all()
            return [message.gql() for message in db_messages]
