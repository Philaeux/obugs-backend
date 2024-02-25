import uuid

import strawberry
from strawberry.types import Info

from obugs.database.user import User
from obugs.database.user_software_role import UserSoftwareRole
from obugs.graphql.types.generated import OBugsError, User as UserGQL
from obugs.utils.helpers import check_user


@strawberry.type
class MutationUser:

    @strawberry.mutation
    async def ban_user(self, info: Info, user_id: uuid.UUID, ban: bool) -> OBugsError | UserGQL:
        current_user = check_user(info.context)
        if current_user is None:
            return OBugsError(message="Not logged client")

        with info.context['session_factory'](expire_on_commit=False) as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
            if db_user is None or not db_user.is_admin:
                return OBugsError(message="User is not admin.")
            if db_user.is_banned:
                return OBugsError(message="Banned user.")

            to_ban = session.query(User).where(User.id == user_id).one_or_none()
            if to_ban is None:
                return OBugsError(message="Target user does not exist.")

            to_ban.is_banned = ban
            session.commit()
            return to_ban

    @strawberry.mutation
    async def change_role(self, info: Info, user_id: uuid.UUID, software_id: str, role: int, set_on: bool) -> OBugsError | UserGQL:
        current_user = check_user(info.context)
        if current_user is None:
            return OBugsError(message="Not logged client")

        with info.context['session_factory'](expire_on_commit=False) as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
            if db_user is None:
                return OBugsError(message="User not allowed to perform.")
            if not db_user.is_admin:
                db_role = db_user.roles.where(UserSoftwareRole.software_id == software_id).one_or_none()
                if db_role is None:
                    return OBugsError(message="User not allowed to perform.")
                if db_role.role & 4 == 0:
                    return OBugsError(message="User not allowed to perform.")

            db_user = session.query(User).where(User.id == user_id).one_or_none()
            if db_user is None:
                return OBugsError(message="Cannot find target user in database.")
            db_role = (session.query(UserSoftwareRole)
                              .filter(UserSoftwareRole.user_id == user_id)
                              .filter(UserSoftwareRole.software_id == software_id)
                              .one_or_none())
            if db_role is None:
                db_role = UserSoftwareRole(software_id=software_id, user_id=user_id, role=0)
                session.add(db_role)
            if set_on:
                db_role.role = db_role.role | role
            else:
                db_role.role = db_role.role & (~role)
            session.commit()
            return db_user
