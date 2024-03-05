import uuid

from strawberry.types import Info

from obugs.database.vote import Vote
from obugs.graphql.types.generated import Vote as VoteGQL
from obugs.utils.helpers import check_user


async def vote_my(info: Info, subject_id: uuid.UUID) -> VoteGQL | None:
    """Get my vote information on a specific subject

    Args:
        info: GraphQL context
        subject_id: Subject to have the user info about
    """
    current_user = check_user(info.context)
    if current_user is None:
        return None

    with info.context['session_factory']() as session:
        db_vote = session.query(Vote).where(Vote.user_id == uuid.UUID(current_user),
                                            Vote.subject_id == subject_id).one_or_none()
        return db_vote
