import asyncio

import strawberry
from sqlalchemy import select

from obugs.database.software import Software
from obugs.graphql.types import Software as SoftwareGQL


@strawberry.type
class QuerySoftware:

    @strawberry.field
    def software(self, info, software_id: str) -> SoftwareGQL | None:
        with info.context['session_factory']() as session:
            db_software = session.query(Software).where(Software.id == software_id).one_or_none()
            return db_software

    @strawberry.field
    def softwares(self, info) -> list[SoftwareGQL]:
        asyncio.get_event_loop()
        with info.context['session_factory']() as session:
            sql = select(Software).order_by(Software.full_name)
            return session.execute(sql).scalars().all()
