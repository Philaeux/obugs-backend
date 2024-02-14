import strawberry
from sqlalchemy import select

from obugs.database.software import Software
from obugs.database.software_suggestion import SoftwareSuggestion
from obugs.graphql.types.generated import Software as SoftwareGQL, SoftwareSuggestion as SoftwareSuggestionGQL

@strawberry.type
class QuerySoftware:

    @strawberry.field
    async def software(self, info, software_id: str) -> SoftwareGQL | None:
        with info.context['session_factory']() as session:
            db_software = session.query(Software).where(Software.id == software_id).one_or_none()
            return db_software

    @strawberry.field
    async def softwares(self, info, search: str | None) -> list[SoftwareGQL]:
        with info.context['session_factory']() as session:
            sql = select(Software)
            if search is not None:
                sql = sql.filter(Software.full_name.ilike(f"%{search}%"))
            sql = sql.order_by(Software.full_name)
            return session.execute(sql).scalars().all()

    @strawberry.field
    async def software_suggestions(self, info) -> list[SoftwareSuggestionGQL]:
        with info.context['session_factory']() as session:
            sql = select(SoftwareSuggestion).limit(50)
            return session.execute(sql).scalars().all()
