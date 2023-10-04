import datetime
import json
import uuid
from typing import Annotated

import requests
import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.database.entry import Entry as EntryEntity, EntryStatus
from obugs.database.entry_message import EntryMessageCreation
from obugs.database.tag import Tag
from obugs.database.user import User
from obugs.database.vote import Vote

from obugs.graphql.types import OBugsError


@strawberry.type
class MutationEntry:

    @strawberry.mutation
    @jwt_required()
    def create_entry(self, info, recaptcha: str, software_id: str, title: str, tags: list[str], description: str,
                     illustration: str) -> OBugsError | Annotated["Entry", strawberry.lazy("..types")]:
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

        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned:
                return OBugsError(message="Banned user.")

            entry = EntryEntity(id=uuid.uuid4(), software_id=software_id, title=title, status=EntryStatus.NEW,
                                description=description, illustration=illustration,
                                created_at=datetime.datetime.utcnow(),
                                updated_at=datetime.datetime.utcnow(), open_patches_count=0)
            for tag in tags:
                tag_entity = session.query(Tag).where(Tag.software_id == software_id,
                                                      Tag.name == tag).one_or_none()
                if tag_entity is not None:
                    entry.tags.append(tag_entity)
            vote = Vote(user_id=db_user.id, subject_id=entry.id, rating=2)
            state_after = json.dumps({
                'title': entry.title,
                'description': entry.description,
                'illustration': entry.illustration,
                'status': str(entry.status.value),
                'tags': [str(tag.name) for tag in entry.tags]
            })
            message = EntryMessageCreation(entry=entry, user_id=db_user.id,
                                           created_at=datetime.datetime.utcnow(), state_after=state_after)
            session.add(entry)
            session.add(vote)
            session.add(message)
            session.commit()
            return entry
