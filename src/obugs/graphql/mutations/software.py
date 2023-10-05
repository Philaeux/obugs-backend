from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.database.user import User
from obugs.database.software import Software
from obugs.graphql.types import OBugsError, Software as SoftwareGQL


@strawberry.type
class MutationSoftware:

    @strawberry.mutation
    @jwt_required()
    def upsert_software(self, info, id: str, full_name: str, editor: str, description: str,
                        language: str) -> OBugsError | SoftwareGQL:
        current_user = get_jwt_identity()

        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == UUID(current_user['id'])).one_or_none()
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
            #return db_software
            return session.query(Software).where(Software.id == id).one_or_none() (1)
