import strawberry
import uuid


@strawberry.type
class Tag:
    id: uuid.UUID
    name: str
    software_id: str
    font_color: str
    background_color: str
