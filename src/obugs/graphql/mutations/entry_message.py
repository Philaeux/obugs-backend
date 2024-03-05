import json
import uuid
from datetime import datetime

import requests
from strawberry.types import Info

from obugs.database.entry import Entry, EntryStatus
from obugs.database.entry_message import EntryMessage, EntryMessagePatch, EntryMessageComment
from obugs.database.tag import Tag
from obugs.database.user import User
from obugs.database.user_software_role import SoftwareRole
from obugs.database.vote import Vote
from obugs.graphql.types.generated import EntryMessageComment as EntryMessageCommentGQL, \
    EntryMessagePatch as EntryMessagePatchGQL
from obugs.graphql.types.generic import ApiSuccess, ProcessPatchSuccess, ApiError
from obugs.utils.helpers import check_user


async def entry_comment(info: Info, recaptcha: str, entry_id: uuid.UUID, comment: str) \
        -> ApiError | EntryMessageCommentGQL:
    current_user = check_user(info.context)
    if current_user is None:
        return ApiError(message="Not logged client")

    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': info.context['settings'].recaptcha,
            'response': recaptcha
        })
        result = response.json()
        if not result['success']:
            return ApiError(message='Invalid recaptcha.')
    except Exception:
        return ApiError(message='Problem while checking recaptcha.')

    if comment == '':
        return ApiError(message="Empty comment")

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_entry = session.query(Entry).where(Entry.id == entry_id).one_or_none()
        if db_entry is None:
            return ApiError(message="Entry doesn't exist anymore.")
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned:
            return ApiError(message="Banned user.")

        message_id = uuid.uuid4()
        message = EntryMessageComment(id=message_id, entry=db_entry, user=db_user,
                                      created_at=datetime.utcnow(),
                                      comment=comment)
        session.add(message)
        db_entry.updated_at = datetime.utcnow()
        db_entry.comment_count = session.query(EntryMessageComment).where(
            EntryMessageComment.entry_id == db_entry.id).count()
        session.commit()

        return message


async def entry_message_delete(info: Info, message_id: uuid.UUID) -> ApiError | ApiSuccess:
    current_user = check_user(info.context)
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned:
            return ApiError(message="Impossible for user to do this action.")

        to_delete = session.query(EntryMessage).where(EntryMessage.id == message_id).one_or_none()
        if to_delete is None:
            return ApiError(message="Target message not found.")

        if not db_user.is_admin and not db_user.is_role_on_software(SoftwareRole.MOD, to_delete.entry.software_id):
            return ApiError(message="Impossible for user to do this action.")

        if to_delete.type == 'patch':
            for vote in session.query(Vote).where(Vote.subject_id == to_delete.id):
                session.delete(vote)
            to_delete.entry.open_patches_count = session.query(EntryMessagePatch).where(
                EntryMessagePatch.entry == to_delete.entry,
                EntryMessagePatch.is_closed is False).count()
        if to_delete.type == 'comment':
            to_delete.entry.comment_count = session.query(EntryMessageComment).where(
                EntryMessageComment.entry == to_delete.entry).count()

        session.delete(to_delete)
        session.commit()
        return ApiSuccess(message="")


async def entry_patch_process(info: Info, message_id: uuid.UUID, accept: bool) -> ApiError | ProcessPatchSuccess:
    current_user = check_user(info.context)
    if current_user is None:
        return ApiError(message="Not logged client")

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned:
            return ApiError(message="Impossible for user to do this action.")

        db_patch = session.query(EntryMessagePatch).where(EntryMessagePatch.id == message_id).one_or_none()
        if db_patch is None or db_patch.type != 'patch' or db_patch.is_closed:
            return ApiError(message="Invalid patch to process.")

        if not db_user.is_admin and not db_user.is_role_on_software(SoftwareRole.CURATOR,
                                                                    db_patch.entry.software_id):
            return ApiError(message="Impossible for user to do this action.")

        db_patch.is_closed = True
        db_patch.accepted = accept
        db_patch.closed_at = datetime.utcnow()
        db_patch.closed_by_id = uuid.UUID(current_user)

        db_patch.entry.updated_at = datetime.utcnow()
        if accept:
            state_before = json.loads(db_patch.state_before)
            state_after = json.loads(db_patch.state_after)
            if 'title' in state_after:
                db_patch.entry.title = state_after['title']
            if 'status' in state_after:
                db_patch.entry.status = EntryStatus[state_after['status']]
            if 'description' in state_after:
                db_patch.entry.description = state_after['description']
            if 'illustration' in state_after:
                db_patch.entry.illustration = state_after['illustration']
            if 'tags' in state_after:
                to_remove = [item for item in state_before['tags'] if item not in state_after['tags']]
                to_add = [item for item in state_after['tags'] if item not in state_before['tags']]
                for tag in to_remove:
                    db_tag = session.query(Tag).where(Tag.software_id == db_patch.entry.software_id,
                                                      Tag.name == tag).one_or_none()
                    if db_tag is not None:
                        db_patch.entry.tags.remove(db_tag)
                for tag in to_add:
                    db_tag = session.query(Tag).where(Tag.software_id == db_patch.entry.software_id,
                                                      Tag.name == tag).one_or_none()
                    if db_tag is not None:
                        db_patch.entry.tags.append(db_tag)

        db_patch.entry.open_patches_count = session.query(EntryMessagePatch).where(
            EntryMessagePatch.entry_id == db_patch.entry.id,
            EntryMessagePatch.is_closed == False).count()
        session.commit()
        len(db_patch.entry.tags)
        return ProcessPatchSuccess(entry_message=db_patch, entry=db_patch.entry)


async def entry_patch_submit(info: Info, recaptcha: str, entry_id: uuid.UUID, title: str, status: str, tags: list[str],
                             description: str, illustration: str) -> ApiError | EntryMessagePatchGQL:
    current_user = check_user(info.context)
    if current_user is None:
        return ApiError(message="Not logged client")

    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': info.context['settings'].recaptcha,
            'response': recaptcha
        })
        result = response.json()
        if not result['success']:
            return ApiError(message='Invalid recaptcha.')
    except Exception:
        return ApiError(message='Problem while checking recaptcha.')

    with info.context['session_factory'](expire_on_commit=False) as session:
        db_entry = session.query(Entry).where(Entry.id == entry_id).one_or_none()
        if db_entry is None:
            return ApiError(message="Entry doesn't exist anymore.")
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned:
            return ApiError(message="Impossible for user to do this action.")

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
        if illustration.strip() != db_entry.illustration:
            state_before['illustration'] = db_entry.illustration
            state_after['illustration'] = illustration.strip()
            is_modified = True
        if set(tags_as_strings) != set(tags):
            state_before['tags'] = tags_as_strings
            state_after['tags'] = tags
            is_modified = True

        if not is_modified:
            return ApiError(message="Patch contains no change.")

        patch_id = uuid.uuid4()
        patch = EntryMessagePatch(
            id=patch_id,
            entry=db_entry,
            user=db_user,
            created_at=datetime.utcnow(),
            state_before=json.dumps(state_before),
            state_after=json.dumps(state_after),
            rating_total=1,
            rating_count=1,
            is_closed=False
        )
        vote = Vote(subject_id=patch.id, user=db_user, rating=1)
        session.add(patch)
        session.add(vote)
        db_entry.updated_at = datetime.utcnow()
        db_entry.open_patches_count = session.query(EntryMessagePatch).where(
            EntryMessagePatch.entry_id == db_entry.id,
            EntryMessagePatch.is_closed == False).count()
        session.commit()

        return patch
