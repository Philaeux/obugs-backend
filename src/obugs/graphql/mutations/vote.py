import uuid
from uuid import UUID

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_entry import EntryEntity
from obugs.database.entity_entry_message import EntryMessagePatchEntity
from obugs.database.entity_user import UserEntity
from obugs.database.entity_vote import VoteEntity
from obugs.graphql.types.composites import VoteUpdate
from obugs.graphql.types.obugs_error import OBugsError


@strawberry.type
class MutationVote:

    @strawberry.mutation
    @jwt_required()
    def vote(self, info, subject_id: uuid.UUID, rating: int) -> OBugsError | VoteUpdate:
        current_user = get_jwt_identity()
        with Session(info.context['engine']) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned:
                return OBugsError(message="Banned user.")

            db_entry = session.query(EntryEntity).where(EntryEntity.id == subject_id).one_or_none()
            db_patch = session.query(EntryMessagePatchEntity).where(
                EntryMessagePatchEntity.id == subject_id).one_or_none()

            if db_entry is not None:
                if rating not in [1, 2, 3, 4, 5]:
                    return OBugsError(message="Invalid vote value.")
                db_vote = session.query(VoteEntity).where(VoteEntity.user_id == db_user.id,
                                                          VoteEntity.subject_id == subject_id).one_or_none()
                if db_vote is None:
                    db_vote = VoteEntity(user_id=db_user.id, subject_id=subject_id, rating=rating)
                    session.add(db_vote)
                    db_entry.rating_count = db_entry.rating_count + 1
                else:
                    db_entry.rating_total = db_entry.rating_total - db_vote.rating
                db_entry.rating_total = db_entry.rating_total + rating
                db_vote.rating = rating
                session.commit()
                return VoteUpdate(rating_count=db_entry.rating_count, rating_total=db_entry.rating_total)
            elif db_patch is not None:
                if rating not in [-1, 1]:
                    return OBugsError(message="Invalid vote value.")
                db_vote = session.query(VoteEntity).where(VoteEntity.user_id == db_user.id,
                                                          VoteEntity.subject_id == subject_id).one_or_none()
                if db_vote is None:
                    db_vote = VoteEntity(user_id=db_user.id, subject_id=subject_id, rating=rating)
                    session.add(db_vote)
                    db_patch.rating_count = db_patch.rating_count + 1
                else:
                    db_patch.rating_total = db_patch.rating_total - db_vote.rating
                db_patch.rating_total = db_patch.rating_total + rating
                db_vote.rating = rating
                session.commit()
                return VoteUpdate(rating_count=db_patch.rating_count, rating_total=db_patch.rating_total)
            return OBugsError(message="No subject found to vote on.")
