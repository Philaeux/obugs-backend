import datetime
import json
import uuid
from uuid import UUID

import requests
import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from obugs.database.database import Database
from obugs.database.entity_entry import EntryEntity, EntryStatus
from obugs.database.entity_entry_message import EntryMessageCreationEntity
from obugs.database.entity_tag import TagEntity
from obugs.database.entity_user import UserEntity
from obugs.database.entity_vote import VoteEntity
from obugs.graphql.types.entry import Entry
from obugs.graphql.types.obugs_error import OBugsError


@strawberry.type
class MutationEntry:

    @strawberry.mutation
    @jwt_required()
    def create_entry(self, info, recaptcha: str, software_id: str, title: str, tags: list[str], description: str,
                     illustration: str) -> OBugsError | Entry:
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
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned:
                return OBugsError(message="Banned user.")

            entry = EntryEntity(id=uuid.uuid4(), software_id=software_id, title=title, status=EntryStatus.NEW,
                                description=description, illustration=illustration,
                                created_at=datetime.datetime.utcnow(),
                                updated_at=datetime.datetime.utcnow(), open_patches_count=0)
            for tag in tags:
                tag_entity = session.query(TagEntity).where(TagEntity.software_id == software_id,
                                                            TagEntity.name == tag).one_or_none()
                if tag_entity is not None:
                    entry.tags.append(tag_entity)
            vote = VoteEntity(user_id=db_user.id, subject_id=entry.id, rating=2)
            state_after = json.dumps({
                'title': entry.title,
                'description': entry.description,
                'illustration': entry.illustration,
                'status': str(entry.status.value),
                'tags': [str(tag.name) for tag in entry.tags]
            })
            message = EntryMessageCreationEntity(entry=entry, user_id=db_user.id,
                                                 created_at=datetime.datetime.utcnow(), state_after=state_after)
            session.add(entry)
            session.add(vote)
            session.add(message)
            session.commit()
            return entry.gql()
