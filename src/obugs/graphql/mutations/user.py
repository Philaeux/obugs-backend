import uuid

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.database.user import User
from obugs.graphql.types import OBugsError, User as UserGQL


@strawberry.type
class MutationUser:

    @strawberry.mutation
    @jwt_required()
    def ban_user(self, info, user_id: uuid.UUID, ban: bool) -> OBugsError | UserGQL:
        current_user = get_jwt_identity()
        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user['id'])).one_or_none()
            if db_user is None or not db_user.is_admin:
                return OBugsError(message="User is not admin.")
            if db_user.is_banned:
                return OBugsError(message="Banned user.")

            to_ban = session.query(User).where(User.id == user_id).one_or_none()
            if to_ban is None:
                return OBugsError(message="Target user does not exist.")

            to_ban.is_banned = ban
            session.commit()
            #return to_ban
            return session.query(User).where(User.id == user_id).one_or_none()
