import strawberry


@strawberry.type
class VoteUpdate:
    rating_total: int
    rating_count: int
