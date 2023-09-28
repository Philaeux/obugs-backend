from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_user import UserEntity
from obugs.database.entity_entry_message import EntryMessageEntity
from obugs.graphql.types.error import Error
from obugs.graphql.types.composites import MessageDeleteSuccess
from obugs.database.entity_vote import VoteEntity


@strawberry.type
class MutationEntryMessage:

    @strawberry.mutation
    @jwt_required()
    def delete_message(self, message_id: UUID) -> Error | MessageDeleteSuccess:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or not db_user.is_admin or db_user.is_banned:
                return Error(message="Impossible for user to do this action.")

            to_delete = session.query(EntryMessageEntity).where(EntryMessageEntity.id == message_id).one_or_none()
            if to_delete is None:
                return Error(message="Target message not found.")

            if to_delete.type == 'patch':
                for vote in session.query(VoteEntity).where(VoteEntity.subject_id == to_delete.id):
                    session.delete(vote)

            session.delete(to_delete)
            session.commit()
            return MessageDeleteSuccess(success=True)
