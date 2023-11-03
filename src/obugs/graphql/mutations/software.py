import uuid
from uuid import UUID

import strawberry
import requests

from obugs.database.user import User
from obugs.database.software import Software
from obugs.database.software_suggestion import SoftwareSuggestion
from obugs.graphql.types import OBugsError, OperationDone, Software as SoftwareGQL, SoftwareSuggestion as SoftwareSuggestionGQL
from obugs.helpers import check_user


@strawberry.type
class MutationSoftware:

    @strawberry.mutation
    async def upsert_software(self, info, id: str, full_name: str, editor: str, description: str,
                              language: str) -> OBugsError | SoftwareGQL:
        current_user = check_user(info.context)
        if current_user is None:
            return OBugsError(message="Not logged client")

        with info.context['session_factory'](expire_on_commit=False) as session:
            db_user = session.query(User).where(User.id == UUID(current_user)).one_or_none()
            if db_user is None or db_user.is_banned or not db_user.is_admin:
                return OBugsError(message="Mutation not allowed for this user.")

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

    @strawberry.mutation
    async def suggest_software(self, info, recaptcha: str, name: str, description: str) -> OBugsError | SoftwareSuggestionGQL:
        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                'secret': info.context['config']['Default']['RECAPTCHA'],
                'response': recaptcha
            })
            result = response.json()
            if not result['success']:
                return OBugsError(message='Invalid recaptcha.')
        except Exception:
            return OBugsError(message='Problem while checking recaptcha.')

        with info.context['session_factory'](expire_on_commit=False) as session:
            db_suggestion = SoftwareSuggestion(id=uuid.uuid4(), name=name, description=description)
            session.add(db_suggestion)
            session.commit()

            return db_suggestion

    @strawberry.mutation
    async def delete_suggestion(self, info, suggestion_id: uuid.UUID) -> OBugsError | OperationDone:
        current_user = check_user(info.context)
        if current_user is None:
            return OBugsError(message="Not logged client")

        with info.context['session_factory'](expire_on_commit=False) as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
            if db_user is None or db_user.is_banned or not db_user.is_admin:
                return OBugsError(message="Impossible for user to do this action.")

            to_delete = session.query(SoftwareSuggestion).where(SoftwareSuggestion.id == suggestion_id).one_or_none()
            if to_delete is None:
                return OBugsError(message="Target message not found.")

            session.delete(to_delete)
            session.commit()
            return OperationDone(success=True)
