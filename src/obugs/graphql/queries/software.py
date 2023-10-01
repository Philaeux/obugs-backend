import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_software import SoftwareEntity
from obugs.graphql.types.software import Software


# noinspection PyArgumentList
@strawberry.type
class QuerySoftware:

    @strawberry.field
    def software(self, software_id: str) -> Software | None:
        with Session(Database().engine) as session:
            db_software = session.query(SoftwareEntity).where(SoftwareEntity.id == software_id).one_or_none()
            if db_software is None:
                return None
            else:
                return db_software.gql()

    @strawberry.field
    def softwares(self) -> list[Software]:
        with Session(Database().engine) as session:
            sql = select(SoftwareEntity).order_by(SoftwareEntity.full_name)
            db_software = session.execute(sql).scalars().all()
            return [software.gql() for software in db_software]
