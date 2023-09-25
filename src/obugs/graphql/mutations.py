import datetime
import json
import uuid
from uuid import UUID

import requests
import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_entry import EntryEntity, EntryStatus
from obugs.database.entity_entry_message import EntryMessageCreationEntity, EntryMessageCommentEntity, \
    EntryMessageEntity, EntryMessagePatchEntity
from obugs.database.entity_tag import TagEntity
from obugs.database.entity_user import UserEntity
from obugs.database.entity_vote import VoteEntity
from obugs.graphql.types.entry import Entry
from obugs.graphql.types.entry_message import EntryMessage
from obugs.graphql.types.vote_update import VoteUpdate


@strawberry.type
class ProcessPatchSuccess:
    entry: Entry
    message: EntryMessage


@strawberry.type
class Mutation:

    @strawberry.mutation
    @jwt_required()
    def create_entry(self, info, recaptcha: str, software_id: str, title: str, tags: list[str], description: str,
                     illustration: str) -> Entry | None:
        current_user = get_jwt_identity()

        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                'secret': info.context['config']['Flask']['RECAPTCHA'],
                'response': recaptcha
            })
            result = response.json()
            if not result['success']:
                return None
        except Exception:
            return None

        with Session(Database().engine) as session:
            entry = EntryEntity(id=uuid.uuid4(), software_id=software_id, title=title, status=EntryStatus.NEW,
                                description=description, illustration=illustration,
                                created_at=datetime.datetime.utcnow(),
                                updated_at=datetime.datetime.utcnow())
            for tag in tags:
                tag_entity = session.query(TagEntity).where(TagEntity.software_id == software_id,
                                                            TagEntity.name == tag).one_or_none()
                if tag_entity is not None:
                    entry.tags.append(tag_entity)
            vote = VoteEntity(user_id=UUID(current_user['id']), subject_id=entry.id, rating=2)
            state_after = json.dumps({
                'title': entry.title,
                'description': entry.description,
                'illustration': entry.illustration,
                'status': str(entry.status.value),
                'tags': [str(tag.name) for tag in entry.tags]
            })
            message = EntryMessageCreationEntity(entry=entry, user_id=UUID(current_user['id']),
                                                 created_at=datetime.datetime.utcnow(), state_after=state_after)
            session.add(entry)
            session.add(vote)
            session.add(message)
            session.commit()
            return entry.gql()

    @strawberry.mutation
    @jwt_required()
    def vote(self, subject_id: uuid.UUID, rating: int) -> VoteUpdate | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == subject_id).one_or_none()
            db_petition = session.query(EntryMessagePatchEntity).where(
                EntryMessagePatchEntity.id == subject_id).one_or_none()

            if db_entry is not None:
                if rating not in [1, 2, 3, 4, 5]:
                    return None
                db_vote = session.query(VoteEntity).where(VoteEntity.user_id == UUID(current_user['id']),
                                                          VoteEntity.subject_id == subject_id).one_or_none()
                if db_vote is None:
                    db_vote = VoteEntity(user_id=UUID(current_user['id']), subject_id=subject_id, rating=rating)
                    session.add(db_vote)
                    db_entry.rating_count = db_entry.rating_count + 1
                else:
                    db_entry.rating_total = db_entry.rating_total - db_vote.rating
                db_entry.rating_total = db_entry.rating_total + rating
                db_vote.rating = rating
                session.commit()
                return VoteUpdate(rating_count=db_entry.rating_count, rating_total=db_entry.rating_total)
            elif db_petition is not None:
                if rating not in [-1, 1]:
                    return None
                db_vote = session.query(VoteEntity).where(VoteEntity.user_id == UUID(current_user['id']),
                                                          VoteEntity.subject_id == subject_id).one_or_none()
                if db_vote is None:
                    db_vote = VoteEntity(user_id=UUID(current_user['id']), subject_id=subject_id, rating=rating)
                    session.add(db_vote)
                    db_petition.rating_count = db_petition.rating_count + 1
                else:
                    db_petition.rating_total = db_petition.rating_total - db_vote.rating
                db_petition.rating_total = db_petition.rating_total + rating
                db_vote.rating = rating
                session.commit()
                return VoteUpdate(rating_count=db_petition.rating_count, rating_total=db_petition.rating_total)
            return None

    @strawberry.mutation
    @jwt_required()
    def comment_entry(self, entry_id: uuid.UUID, comment: str) -> list[EntryMessage]:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return []

            message = EntryMessageCommentEntity(entry=db_entry, user_id=UUID(current_user['id']),
                                                created_at=datetime.datetime.utcnow(),
                                                comment=comment)
            session.add(message)
            db_entry.updated_at = datetime.datetime.utcnow()
            session.commit()
            sql = select(EntryMessageEntity) \
                .where(EntryMessageEntity.entry_id == entry_id) \
                .order_by(EntryMessageEntity.created_at) \
                .limit(20)
            db_messages = session.execute(sql).scalars().all()
            return [message.gql() for message in db_messages]

    @strawberry.mutation
    @jwt_required()
    def submit_proposition(self, entry_id: uuid.UUID, title: str, status: str, tags: list[str], description: str,
                           illustration: str) -> list[EntryMessage]:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return []

            state_before = {}
            state_after = {}
            is_modified = False

            tags_as_strings = []
            for tag in db_entry.tags:
                tags_as_strings.append(tag.name)

            if title != db_entry.title:
                state_before['title'] = db_entry.title
                state_after['title'] = title
                is_modified = True
            if status != db_entry.status.value:
                state_before['status'] = db_entry.status.value
                state_after['status'] = status
                is_modified = True
            if description != db_entry.description:
                state_before['description'] = db_entry.description
                state_after['description'] = description
                is_modified = True
            if illustration != db_entry.illustration:
                state_before['illustration'] = db_entry.illustration
                state_after['illustration'] = illustration
                is_modified = True
            if set(tags_as_strings) != set(tags):
                state_before['tags'] = tags_as_strings
                state_after['tags'] = tags
                is_modified = True

            if not is_modified:
                return []

            proposition = EntryMessagePatchEntity(
                id=uuid.uuid4(),
                entry=db_entry,
                user_id=UUID(current_user['id']),
                created_at=datetime.datetime.utcnow(),
                state_before=json.dumps(state_before),
                state_after=json.dumps(state_after),
                rating_total=1,
                rating_count=1,
                is_closed=False
            )
            vote = VoteEntity(
                subject_id=proposition.id,
                user_id=UUID(current_user['id']),
                rating=1
            )
            db_entry.updated_at = datetime.datetime.utcnow()
            session.add(proposition)
            session.add(vote)
            session.commit()

            sql = select(EntryMessageEntity) \
                .where(EntryMessageEntity.entry_id == entry_id) \
                .order_by(EntryMessageEntity.created_at) \
                .limit(20)
            db_messages = session.execute(sql).scalars().all()
            return [message.gql() for message in db_messages]

    @strawberry.mutation
    @jwt_required()
    def process_patch(self, message_id: uuid.UUID, accept: bool) -> ProcessPatchSuccess | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or not db_user.is_admin:
                return None

            db_message = session.query(EntryMessagePatchEntity).where(
                EntryMessagePatchEntity.id == message_id).one_or_none()
            if db_message is None or db_message.type != 'patch' or db_message.is_closed:
                return None

            db_message.is_closed = True
            db_message.accepted = accept
            db_message.closed_at = datetime.datetime.utcnow()
            db_message.closed_by_id = UUID(current_user['id'])

            db_message.entry.updated_at = datetime.datetime.utcnow()
            if accept:
                state_before = json.loads(db_message.state_before)
                state_after = json.loads(db_message.state_after)
                if 'title' in state_after:
                    db_message.entry.title = state_after['title']
                if 'status' in state_after:
                    db_message.entry.status = EntryStatus[state_after['status']]
                if 'description' in state_after:
                    db_message.entry.description = state_after['description']
                if 'illustration' in state_after:
                    db_message.entry.description = state_after['illustration']
                if 'tags' in state_after:
                    to_remove = [item for item in state_before['tags'] if item not in state_after['tags']]
                    to_add = [item for item in state_after['tags'] if item not in state_before['tags']]
                    for tag in to_remove:
                        db_tag = session.query(TagEntity).where(TagEntity.software_id == db_message.entry.software_id,
                                                                TagEntity.name == tag).one_or_none()
                        if db_tag is not None:
                            db_message.entry.tags.remove(db_tag)
                    for tag in to_add:
                        db_tag = session.query(TagEntity).where(TagEntity.software_id == db_message.entry.software_id,
                                                                TagEntity.name == tag).one_or_none()
                        if db_tag is not None:
                            db_message.entry.tags.append(db_tag)
            session.commit()

            return ProcessPatchSuccess(message=db_message.gql(), entry=db_message.entry.gql())
