import uuid

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.database.user import User
from obugs.graphql.types import OBugsError, User as UserGQL


@strawberry.type
class QueryUser:

    @strawberry.field
    @jwt_required()
    def current_user(self, info) -> OBugsError | UserGQL:
        current_user = get_jwt_identity()
        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user['id'])).one_or_none()
            if db_user is None:
                return OBugsError(message="No user found with specified id.")
            if db_user.is_banned:
                return OBugsError(message="User is banned.")
            return db_user

    @strawberry.field
    def user(self, info, user_id: uuid.UUID) -> UserGQL | None:
        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == user_id).one_or_none()
            return db_user
