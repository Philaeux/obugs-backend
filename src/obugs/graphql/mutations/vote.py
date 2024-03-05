import uuid

import strawberry
from strawberry.types import Info

from obugs.database.entry import Entry
from obugs.database.entry_message import EntryMessagePatch
from obugs.database.user import User
from obugs.database.vote import Vote
from obugs.graphql.types.generic import ApiError
from obugs.utils.helpers import check_user


@strawberry.type
class OutputVote:
    rating_total: int
    rating_count: int


async def vote(info: Info, subject_id: uuid.UUID, rating: int) -> ApiError | OutputVote:
    current_user = check_user(info.context)
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory']() as session:
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned:
            return ApiError(message="Banned user.")

        db_entry = session.query(Entry).where(Entry.id == subject_id).one_or_none()
        db_patch = session.query(EntryMessagePatch).where(
            EntryMessagePatch.id == subject_id).one_or_none()

        if db_entry is not None:
            if rating not in [1, 2, 3, 4, 5]:
                return ApiError(message="Invalid vote value.")
            db_vote = session.query(Vote).where(Vote.user_id == db_user.id,
                                                Vote.subject_id == subject_id).one_or_none()
            if db_vote is None:
                db_vote = Vote(user=db_user, subject_id=subject_id, rating=rating)
                session.add(db_vote)
                db_entry.rating_count = db_entry.rating_count + 1
            else:
                db_entry.rating_total = db_entry.rating_total - db_vote.rating
            db_entry.rating_total = db_entry.rating_total + rating
            db_vote.rating = rating
            session.commit()
            return OutputVote(rating_count=db_entry.rating_count, rating_total=db_entry.rating_total)
        elif db_patch is not None:
            if rating not in [-1, 1]:
                return ApiError(message="Invalid vote value.")
            db_vote = session.query(Vote).where(Vote.user_id == db_user.id,
                                                Vote.subject_id == subject_id).one_or_none()
            if db_vote is None:
                db_vote = Vote(user=db_user, subject_id=subject_id, rating=rating)
                session.add(db_vote)
                db_patch.rating_count = db_patch.rating_count + 1
            else:
                db_patch.rating_total = db_patch.rating_total - db_vote.rating
            db_patch.rating_total = db_patch.rating_total + rating
            db_vote.rating = rating
            session.commit()
            return OutputVote(rating_count=db_patch.rating_count, rating_total=db_patch.rating_total)
        return ApiError(message="No subject found to vote on.")
