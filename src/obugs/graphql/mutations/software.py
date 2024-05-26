import uuid
from uuid import UUID

import strawberry
from strawberry.types import Info
import requests

from obugs.database.user import User
from obugs.database.software import Software
from obugs.database.software_suggestion import SoftwareSuggestion
from obugs.graphql.types.generated import Software as SoftwareGQL, SoftwareSuggestion as SoftwareSuggestionGQL
from obugs.graphql.types.generic import ApiSuccess, ApiError
from obugs.utils.helpers import check_user


async def software_suggest(info: Info, recaptcha: str, name: str, description: str) -> ApiError | SoftwareSuggestionGQL:
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': info.context['settings'].recaptcha,
            'response': recaptcha
        })
        result = response.json()
        if not result['success']:
            return ApiError(message='Invalid recaptcha.')
    except Exception:
        return ApiError(message='Problem while checking recaptcha.')

    current_user = check_user(info.context["settings"].jwt_secret_key,
                              info.context["request"].headers.get("Authorization"))
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_suggestion = SoftwareSuggestion(id=uuid.uuid4(), user_id=current_user, name=name, description=description)
        session.add(db_suggestion)
        session.commit()

        return db_suggestion


async def software_suggestion_delete(info: Info, suggestion_id: uuid.UUID) -> ApiError | ApiSuccess:
    current_user = check_user(info.context["settings"].jwt_secret_key,
                              info.context["request"].headers.get("Authorization"))
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned or not db_user.is_admin:
            return ApiError(message="Impossible for user to do this action.")

        to_delete = session.query(SoftwareSuggestion).where(SoftwareSuggestion.id == suggestion_id).one_or_none()
        if to_delete is None:
            return ApiError(message="Target message not found.")

        session.delete(to_delete)
        session.commit()
        return ApiSuccess(message="")


async def software_upsert(info: Info, id: str, full_name: str, editor: str, description: str,
                          language: str) -> ApiError | SoftwareGQL:
    current_user = check_user(info.context["settings"].jwt_secret_key,
                              info.context["request"].headers.get("Authorization"))
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_user = session.query(User).where(User.id == UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned or not db_user.is_admin:
            return ApiError(message="Mutation not allowed for this user.")

        db_software = session.query(Software).where(Software.id == id).one_or_none()
        if db_software is None:
            db_software = Software(id=id)
            session.add(db_software)
        db_software.full_name = full_name
        db_software.editor = editor
        db_software.description = description
        db_software.language = language
        session.commit()
        return db_software
