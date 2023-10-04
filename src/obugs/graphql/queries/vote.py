import uuid
from typing import Annotated

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.database.vote import Vote


# noinspection PyArgumentList
@strawberry.type
class QueryVote:

    @strawberry.field
    @jwt_required()
    def my_vote(self, info, subject_id: uuid.UUID) -> Annotated["Vote", strawberry.lazy("..types")] | None:
        current_user = get_jwt_identity()
        with info.context['session_factory']() as session:
            db_vote = session.query(Vote).where(Vote.user_id == uuid.UUID(current_user['id']),
                                                Vote.subject_id == subject_id).one_or_none()
            return db_vote
