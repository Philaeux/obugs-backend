import strawberry
from sqlalchemy import select

from obugs.database.tag import Tag
from obugs.graphql.types import Tag as TagGQL


@strawberry.type
class QueryTag:

    @strawberry.field
    async def tags(self, info, software_id: str, search: str | None) -> list[TagGQL]:
        with info.context['session_factory']() as session:
            sql = select(Tag).where(Tag.software_id == software_id)

            if search is not None:
                sql = sql.filter(Tag.name.ilike(f"%{search}%"))

            sql = sql.order_by(Tag.name)
            return session.execute(sql).scalars().all()
