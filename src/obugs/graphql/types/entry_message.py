import datetime
import strawberry
import uuid


@strawberry.type
class EntryMessage:
    id: uuid.UUID
    entry_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    type: str
    comment: str | None
    state_before: str | None
    state_after: str | None
    rating_total: int | None
    rating_count: int | None
    is_closed: bool | None
    closed_at: datetime.datetime | None
    closed_by_id: uuid.UUID | None
    accepted: bool | None
