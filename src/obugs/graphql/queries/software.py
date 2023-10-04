from typing import Annotated

import strawberry
from sqlalchemy import select

from obugs.database.software import Software


# noinspection PyArgumentList
@strawberry.type
class QuerySoftware:

    @strawberry.field
    def software(self, info, software_id: str) -> Annotated["Software", strawberry.lazy("..types")] | None:
        with info.context['session_factory']() as session:
            db_software = session.query(Software).where(Software.id == software_id).one_or_none()
            if db_software is None:
                return None
            else:
                return db_software

    @strawberry.field
    def softwares(self, info) -> list[Annotated["Software", strawberry.lazy("..types")]]:
        with info.context['session_factory']() as session:
            sql = select(Software).order_by(Software.full_name)
            return session.execute(sql).scalars().all()
