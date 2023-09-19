import strawberry


@strawberry.type
class EntryVote:
    id: int
    entry_id: int
    user_id: str
    rating: int
