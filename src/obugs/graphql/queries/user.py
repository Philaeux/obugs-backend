import uuid

from sqlalchemy import or_
from strawberry.types import Info

from obugs.database.user import User
from obugs.graphql.types.generated import User as UserGQL
from obugs.graphql.types.generic import ApiError
from obugs.utils.helpers import check_user


async def user(info: Info, user_id: uuid.UUID) -> UserGQL | None:
    with info.context['session_factory']() as session:
        db_user = session.query(User).where(User.id == user_id).one_or_none()
        return db_user


async def user_current(info: Info) -> ApiError | UserGQL:
    current_user = check_user(info.context)
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory']() as session:
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None:
            return ApiError(message="No user found with specified id.")
        if db_user.is_banned:
            return ApiError(message="User is banned.")
        return db_user


async def users(info: Info, search: str | None) -> list[UserGQL]:
    with info.context['session_factory']() as session:
        db_users = session.query(User)

        if search is not None:
            db_users = db_users.filter(or_(
                User.reddit_name.ilike(f"%{search}%"),
                User.github_name.ilike(f"%{search}%")
            ))
        db_users.limit(50)

    return db_users
