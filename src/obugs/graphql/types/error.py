import strawberry


@strawberry.type
class Error:
    message: str
