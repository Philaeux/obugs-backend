import datetime
import json
import uuid

import requests
from strawberry.types import Info

from obugs.database.entry import Entry, EntryStatus
from obugs.database.entry_message import EntryMessageCreation
from obugs.database.tag import Tag
from obugs.database.user import User
from obugs.database.vote import Vote
from obugs.graphql.types.generated import Entry as EntryGQL
from obugs.graphql.types.generic import ApiError
from obugs.utils.helpers import check_user


async def entry_create(info: Info, recaptcha: str, software_id: str, title: str, tags: list[str], description: str,
                       illustration: str) -> ApiError | EntryGQL:
    current_user = check_user(info.context["settings"].jwt_secret_key,
                              info.context["request"].headers.get("Authorization"))
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
        db_user = session.query(User).where(User.id == uuid.UUID(current_user)).one_or_none()
        if db_user is None or db_user.is_banned:
            return ApiError(message="Banned user.")

        entry_id = uuid.uuid4()
        entry = Entry(id=entry_id, software_id=software_id, title=title,
                      description=description, illustration=illustration.strip(), status=EntryStatus.NEW,
                      rating=2, rating_total=2, rating_count=1, created_at=datetime.datetime.utcnow(),
                      updated_at=datetime.datetime.utcnow(), open_patches_count=0, comment_count=0)
        for tag in tags:
            tag_entity = session.query(Tag).where(Tag.software_id == software_id,
                                                  Tag.name == tag).one_or_none()
            if tag_entity is not None:
                entry.tags.append(tag_entity)
        vote = Vote(user=db_user, subject_id=entry.id, rating=2)
        state_after = json.dumps({
            'title': entry.title,
            'description': entry.description,
            'illustration': entry.illustration,
            'status': str(entry.status.value),
            'tags': [str(tag.name) for tag in entry.tags]
        })
        message = EntryMessageCreation(entry=entry, user=db_user,
                                       created_at=datetime.datetime.utcnow(), state_after=state_after)
        session.add(entry)
        session.add(vote)
        session.add(message)
        session.commit()
        return entry
