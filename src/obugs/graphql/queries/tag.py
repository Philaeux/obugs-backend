from typing import Annotated

import strawberry
from sqlalchemy import select

from obugs.database.tag import Tag


# noinspection PyArgumentList
@strawberry.type
class QueryTag:

    @strawberry.field
    def tags(self, info, software_id: str) -> list[Annotated["Tag", strawberry.lazy("..types")]]:
        with info.context['session_factory']() as session:
            sql = select(Tag).where(Tag.software_id == software_id).order_by(Tag.name)
            return session.execute(sql).scalars().all()
