from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_user import UserEntity
from obugs.database.entity_software import SoftwareEntity
from obugs.graphql.types.software import Software
from obugs.graphql.types.obugs_error import OBugsError


@strawberry.type
class MutationSoftware:

    @strawberry.mutation
    @jwt_required()
    def upsert_software(self, info, id: str, full_name: str, editor: str, description: str, language: str) -> OBugsError | Software:
        current_user = get_jwt_identity()

        with Session(info.context['engine']) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned or not db_user.is_admin:
                return OBugsError(message="Mutation not allowed for this user.")

            db_software = session.query(SoftwareEntity).where(SoftwareEntity.id == id).one_or_none()
            if db_software is None:
                db_software = SoftwareEntity(id=id)
                session.add(db_software)
            db_software.full_name = full_name
            db_software.editor = editor
            db_software.description = description
            db_software.language = language
            session.commit()
            return db_software.gql()
