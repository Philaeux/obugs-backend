import uuid
from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_vote import VoteEntity
from obugs.graphql.types.vote import Vote


# noinspection PyArgumentList
@strawberry.type
class QueryVote:

    @strawberry.field
    @jwt_required()
    def my_vote(self, subject_id: uuid.UUID) -> Vote | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_vote = session.query(VoteEntity).where(VoteEntity.user_id == UUID(current_user['id']),
                                                      VoteEntity.subject_id == subject_id).one_or_none()
            if db_vote is None:
                return None
            else:
                return db_vote.gql()
