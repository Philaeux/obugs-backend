import uuid
from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_user import UserEntity
from obugs.graphql.types.obugs_error import OBugsError
from obugs.graphql.types.user import User


@strawberry.type
class MutationUser:

    @strawberry.mutation
    @jwt_required()
    def ban_user(self, user_id: uuid.UUID, ban: bool) -> OBugsError | User:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or not db_user.is_admin:
                return OBugsError(message="User is not admin.")
            if db_user.is_banned:
                return OBugsError(message="Banned user.")

            to_ban = session.query(UserEntity).where(UserEntity.id == user_id).one_or_none()
            if to_ban is None:
                return OBugsError(message="Target user does not exist.")

            to_ban.is_banned = ban
            session.commit()
            return to_ban.gql()
