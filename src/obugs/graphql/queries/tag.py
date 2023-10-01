import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_tag import TagEntity
from obugs.graphql.types.tag import Tag


# noinspection PyArgumentList
@strawberry.type
class QueryTag:

    @strawberry.field
    def tags(self, software_id: str) -> list[Tag]:
        with Session(Database().engine) as session:
            sql = select(TagEntity).where(TagEntity.software_id == software_id).order_by(TagEntity.name)
            db_tag = session.execute(sql).scalars().all()
            return [tag.gql() for tag in db_tag]
