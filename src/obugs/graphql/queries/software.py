from sqlalchemy import select
from strawberry.types import Info

from obugs.database.software import Software
from obugs.database.software_suggestion import SoftwareSuggestion
from obugs.graphql.types.generated import Software as SoftwareGQL, SoftwareSuggestion as SoftwareSuggestionGQL


async def software(info: Info, software_id: str) -> SoftwareGQL | None:
    with info.context['session_factory']() as session:
        db_software = session.query(Software).where(Software.id == software_id).one_or_none()
        return db_software


async def softwares(info: Info, search: str | None) -> list[SoftwareGQL]:
    with info.context['session_factory']() as session:
        sql = select(Software)
        if search is not None:
            sql = sql.filter(Software.full_name.ilike(f"%{search}%"))
        sql = sql.order_by(Software.full_name)
        return session.execute(sql).scalars().all()


async def software_suggestions(info: Info) -> list[SoftwareSuggestionGQL]:
    with info.context['session_factory']() as session:
        sql = select(SoftwareSuggestion).limit(50)
        return session.execute(sql).scalars().all()
