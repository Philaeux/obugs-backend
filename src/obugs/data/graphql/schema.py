from typing import Optional

import strawberry
from sqlalchemy.orm.session import Session
from sqlalchemy import select
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.data.database.database import Database
from obugs.data.database.entity_software import SoftwareEntity


@strawberry.type
class User:
    id: int
    username: str


@strawberry.type()
class Software:
    id: str
    full_name: str
    editor: str

    @staticmethod
    def sqla(entity: SoftwareEntity) -> Optional["Software"]:
        if entity is None:
            return None
        return Software(
            id=entity.id,
            full_name=entity.full_name,
            editor=entity.editor
        )


@strawberry.type
class Query:

    @strawberry.field
    def softwares(self) -> list[Software]:
        with Session(Database().engine) as session:
            sql = select(SoftwareEntity)
            db_software = session.execute(sql).scalars().all()
            return [Software.sqla(software) for software in db_software]

    @strawberry.field
    def software(self, id: str) -> Software | None:
        with Session(Database().engine) as session:
            sql = select(SoftwareEntity).where(SoftwareEntity.id == id)
            db_software = session.scalar(sql)
            return Software.sqla(db_software)


@strawberry.type
class Mutation:

    @strawberry.mutation
    @jwt_required()
    def say_hello(self) -> str:
        current_user = get_jwt_identity()
        return f"Hello, World! (Authorized user: {current_user})"


schema = strawberry.Schema(query=Query, mutation=Mutation)