from datetime import datetime
import json
import uuid
from uuid import UUID

import requests
import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_tag import TagEntity
from obugs.database.entity_user import UserEntity
from obugs.database.entity_entry import EntryEntity, EntryStatus
from obugs.database.entity_entry_message import EntryMessageEntity, EntryMessagePatchEntity, EntryMessageCommentEntity
from obugs.graphql.types.entry_message import EntryMessage
from obugs.graphql.types.obugs_error import OBugsError
from obugs.graphql.types.composites import MessageDeleteSuccess, ProcessPatchSuccess
from obugs.database.entity_vote import VoteEntity


@strawberry.type
class MutationEntryMessage:

    @strawberry.mutation
    @jwt_required()
    def comment_entry(self, info, recaptcha: str, entry_id: UUID, comment: str) -> OBugsError | EntryMessage:
        current_user = get_jwt_identity()

        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                'secret': info.context['config']['Flask']['RECAPTCHA'],
                'response': recaptcha
            })
            result = response.json()
            if not result['success']:
                return OBugsError(message='Invalid recaptcha.')
        except Exception:
            return OBugsError(message='Problem while checking recaptcha.')

        if comment == '':
            return OBugsError(message="Empty comment")

        with Session(info.context['engine']) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return OBugsError(message="Entry doesn't exist anymore.")
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned:
                return OBugsError(message="Banned user.")

            message = EntryMessageCommentEntity(entry=db_entry, user_id=db_user.id,
                                                created_at=datetime.utcnow(),
                                                comment=comment)
            session.add(message)
            db_entry.updated_at = datetime.utcnow()
            session.commit()
            return message.gql()

    @strawberry.mutation
    @jwt_required()
    def delete_message(self, info, message_id: UUID) -> OBugsError | MessageDeleteSuccess:
        current_user = get_jwt_identity()
        with Session(info.context['engine']) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or not db_user.is_admin or db_user.is_banned:
                return OBugsError(message="Impossible for user to do this action.")

            to_delete = session.query(EntryMessageEntity).where(EntryMessageEntity.id == message_id).one_or_none()
            if to_delete is None:
                return OBugsError(message="Target message not found.")

            if to_delete.type == 'patch':
                for vote in session.query(VoteEntity).where(VoteEntity.subject_id == to_delete.id):
                    session.delete(vote)
                to_delete.entry.open_patches_count = session.query(EntryMessagePatchEntity).where(
                    EntryMessagePatchEntity.is_closed is False).count()

            session.delete(to_delete)
            session.commit()
            return MessageDeleteSuccess(success=True)

    @strawberry.mutation
    @jwt_required()
    def submit_patch(self, info, recaptcha: str, entry_id: uuid.UUID, title: str, status: str, tags: list[str],
                     description: str, illustration: str) -> OBugsError | EntryMessage:
        current_user = get_jwt_identity()

        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                'secret': info.context['config']['Flask']['RECAPTCHA'],
                'response': recaptcha
            })
            result = response.json()
            if not result['success']:
                return OBugsError(message='Invalid recaptcha.')
        except Exception:
            return OBugsError(message='Problem while checking recaptcha.')

        with Session(info.context['engine']) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return OBugsError(message="Entry doesn't exist anymore.")
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned:
                return OBugsError(message="Banned user.")

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
                return OBugsError(message="Patch contains no change.")

            patch = EntryMessagePatchEntity(
                id=uuid.uuid4(),
                entry=db_entry,
                user_id=db_user.id,
                created_at=datetime.utcnow(),
                state_before=json.dumps(state_before),
                state_after=json.dumps(state_after),
                rating_total=1,
                rating_count=1,
                is_closed=False
            )
            vote = VoteEntity(
                subject_id=patch.id,
                user_id=db_user.id,
                rating=1
            )
            db_entry.updated_at = datetime.utcnow()
            db_entry.open_patches_count = session.query(EntryMessagePatchEntity).where(
                EntryMessagePatchEntity.entry_id == db_entry.id,
                EntryMessagePatchEntity.is_closed == False).count() + 1
            session.add(patch)
            session.add(vote)
            session.commit()

            return patch.gql()

    @strawberry.mutation
    @jwt_required()
    def process_patch(self, info, message_id: uuid.UUID, accept: bool) -> OBugsError | ProcessPatchSuccess:
        current_user = get_jwt_identity()
        with Session(info.context['engine']) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or not db_user.is_admin:
                return OBugsError(message="User is not admin.")
            if db_user is None or db_user.is_banned:
                return OBugsError(message="Banned user.")

            db_message = session.query(EntryMessagePatchEntity).where(
                EntryMessagePatchEntity.id == message_id).one_or_none()
            if db_message is None or db_message.type != 'patch' or db_message.is_closed:
                return OBugsError(message="Invalid patch to process.")

            db_message.is_closed = True
            db_message.accepted = accept
            db_message.closed_at = datetime.utcnow()
            db_message.closed_by_id = UUID(current_user['id'])

            db_message.entry.updated_at = datetime.utcnow()
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
                    db_message.entry.illustration = state_after['illustration']
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

            db_message.entry.open_patches_count = session.query(EntryMessagePatchEntity).where(
                EntryMessagePatchEntity.entry_id == db_message.entry.id,
                EntryMessagePatchEntity.is_closed == False).count()
            session.commit()

            return ProcessPatchSuccess(entry_message=db_message.gql(), entry=db_message.entry.gql())
