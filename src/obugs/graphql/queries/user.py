import uuid

import strawberry
from strawberry.types import Info

from sqlalchemy import or_

from obugs.database.user import User
from obugs.graphql.types.generated import OBugsError, User as UserGQL
from obugs.utils.helpers import check_user


@strawberry.type
class QueryUser:

    @strawberry.field
    async def current_user(self, info: Info) -> OBugsError | UserGQL:
        current_user = check_user(info.context)
        if current_user is None:
            return OBugsError(message="Not logged client")

        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
            if db_user is None:
                return OBugsError(message="No user found with specified id.")
            if db_user.is_banned:
                return OBugsError(message="User is banned.")
            return db_user

    @strawberry.field
    async def user(self, info: Info, user_id: uuid.UUID) -> UserGQL | None:
        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == user_id).one_or_none()
            return db_user

    @strawberry.field
    async def users(self, info: Info, search: str | None) -> list[UserGQL]:
        with info.context['session_factory']() as session:
            db_users = session.query(User)

            if search is not None:
                db_users = db_users.filter(or_(
                    User.reddit_name.ilike(f"%{search}%"),
                    User.github_name.ilike(f"%{search}%")
                ))
            db_users.limit(50)

        return db_users
