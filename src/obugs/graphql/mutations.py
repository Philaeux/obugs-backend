import datetime

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_entry import EntryEntity, EntryStatus
from obugs.database.entity_entry_message import EntryMessageCreationEntity
from obugs.database.entity_entry_vote import EntryVoteEntity
from obugs.database.entity_tag import TagEntity
from obugs.graphql.types.entry import Entry


@strawberry.type
class Mutation:

    @strawberry.mutation
    @jwt_required()
    def create_entry(self, software_id: str, title: str, tags: list[str], description: str, illustration: str) -> Entry:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            entry = EntryEntity(software_id=software_id, title=title, status=EntryStatus.NEW,
                                description=description, illustration=illustration,
                                created_at=datetime.datetime.utcnow(),
                                updated_at=datetime.datetime.utcnow())
            for tag in tags:
                tag_entity = session.query(TagEntity).where(TagEntity.software_id == software_id,
                                                            TagEntity.name == tag).one_or_none()
                if tag_entity is not None:
                    entry.tags.append(tag_entity)
            session.add(entry)
            vote = EntryVoteEntity(user_id=current_user['id'], entry=entry, rating=2)
            message = EntryMessageCreationEntity(entry=entry, user_id=current_user['id'],
                                                 created_at=datetime.datetime.utcnow(),
                                                 state_after=entry.export_snapshot())
            session.add(vote)
            session.add(message)
            session.commit()
            return entry.gql()

    @strawberry.mutation
    @jwt_required()
    def vote_on_entry(self, entry_id: int, rating: int) -> Entry | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return None
            sanitize_rating = min(5, max(1, rating))

            db_vote = session.query(EntryVoteEntity).where(EntryVoteEntity.user_id == current_user['id'],
                                                           EntryVoteEntity.entry_id == entry_id).one_or_none()
            if db_vote is None:
                db_vote = EntryVoteEntity(user_id=current_user['id'], entry_id=entry_id, rating=sanitize_rating)
                session.add(db_vote)
                db_entry.rating_count = db_entry.rating_count + 1
            else:
                db_entry.rating_total = db_entry.rating_total - db_vote.rating
            db_vote.rating = sanitize_rating
            db_entry.rating_total = db_entry.rating_total + sanitize_rating
            session.commit()
            return db_entry.gql()
