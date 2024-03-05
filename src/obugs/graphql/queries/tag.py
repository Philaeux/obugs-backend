from strawberry.types import Info

from obugs.database.tag import Tag
from obugs.graphql.types.generated import Tag as TagGQL


async def tags(info: Info, software_id: str, search: str | None) -> list[TagGQL]:
    with info.context['session_factory']() as session:
        sql = session.query(Tag).where(Tag.software_id == software_id)

        if search is not None:
            sql = sql.filter(Tag.name.ilike(f"%{search}%"))

        sql = sql.order_by(Tag.name)
        return session.execute(sql).scalars().all()
