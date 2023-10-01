import uuid
from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_user import UserEntity
from obugs.graphql.types.obugs_error import OBugsError
from obugs.graphql.types.user import User


# noinspection PyArgumentList
@strawberry.type
class QueryUser:

    @strawberry.field
    @jwt_required()
    def current_user(self) -> OBugsError | User:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None:
                return OBugsError(message="No user found with specified id.")
            if db_user.is_banned:
                return OBugsError(message="User is banned.")
            return db_user.gql()

    @strawberry.field
    def user(self, user_id: uuid.UUID) -> User | None:
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == user_id).one_or_none()
            if db_user is None:
                return None
            else:
                return db_user.gql()
