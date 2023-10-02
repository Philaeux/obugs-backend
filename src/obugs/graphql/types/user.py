import strawberry
import uuid


@strawberry.type
class User:
    id: uuid.UUID
    username: str
    is_admin: bool
    is_banned: bool
    software_is_mod: list[str]
    software_is_curator: list[str]
    software_is_editor: list[str]
