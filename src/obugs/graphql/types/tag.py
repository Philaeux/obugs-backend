import strawberry


@strawberry.type
class Tag:
    id: int
    name: str
    software_id: str
    font_color: str
    background_color: str
