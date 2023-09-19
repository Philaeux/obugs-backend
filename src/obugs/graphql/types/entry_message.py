import datetime
import strawberry


@strawberry.type
class EntryMessage:
    id: int
    entry_id: int
    user_id: int
    created_at: datetime.datetime
    type: str
    comment: str | None
    state_before: str | None
    state_after: str | None
    rating: int | None
    rating_count: int | None
