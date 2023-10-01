import datetime
import strawberry
import uuid

from obugs.graphql.types.tag import Tag


@strawberry.type
class Entry:
    id: uuid.UUID
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
    open_patches_count: int
