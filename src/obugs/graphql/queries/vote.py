import uuid

import strawberry

from obugs.database.vote import Vote
from obugs.graphql.types import Vote as VoteGQL
from obugs.helpers import check_user


@strawberry.type
class QueryVote:

    @strawberry.field
    def my_vote(self, info, subject_id: uuid.UUID) -> VoteGQL | None:
        current_user = check_user(info.context)
        if current_user is None:
            return None

        with info.context['session_factory']() as session:
            db_vote = session.query(Vote).where(Vote.user_id == uuid.UUID(current_user),
                                                Vote.subject_id == subject_id).one_or_none()
            return db_vote
