import datetime
import strawberry

from obugs.graphql.types.tag import Tag


@strawberry.type
class Entry:
    id: int
    software_id: str
    title: str
    tags: list[Tag]
    description: str
    illustration: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str
    rating_total: int
    rating_count: int
