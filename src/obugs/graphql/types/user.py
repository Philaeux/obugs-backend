import strawberry
import uuid


@strawberry.type
class User:
    id: uuid.UUID
    username: str
    is_admin: bool
    is_banned: bool
