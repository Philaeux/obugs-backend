import strawberry
import uuid


@strawberry.type
class Vote:
    id: uuid.UUID
    subject_id: uuid.UUID
    user_id: uuid.UUID
    rating: int
