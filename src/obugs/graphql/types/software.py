import strawberry


@strawberry.type
class Software:
    id: str
    full_name: str
    editor: str
    description: str
    language: str
