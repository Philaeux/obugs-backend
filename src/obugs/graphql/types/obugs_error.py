import strawberry


@strawberry.type
class OBugsError:
    message: str
