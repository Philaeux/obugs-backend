import uuid

import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.database.user import User
from obugs.database.software import Software
from obugs.database.tag import Tag
from obugs.graphql.types import OBugsError, Tag as TagGQL


@strawberry.type
class MutationTag:

    @strawberry.mutation
    @jwt_required()
    def upsert_tag(self, info, id: uuid.UUID | None, software_id: str, name: str, font_color: str, background_color: str) -> OBugsError | TagGQL:
        current_user = get_jwt_identity()

        with info.context['session_factory']() as session:
            db_user = session.query(User).where(User.id == uuid.UUID(current_user['id'])).one_or_none()
            if db_user is None or db_user.is_banned or not db_user.is_admin:
                return OBugsError(message="Mutation not allowed for this user.")

            db_software = session.query(Software).where(Software.id == software_id).one_or_none()
            if db_software is None:
                return OBugsError(message="No Software with this id.")

            if id is not None:
                db_tag = session.query(Tag).where(Tag.id == id).one_or_none()
                if db_tag is None:
                    return OBugsError(message="No such tag to edit.")
                db_tag.software_id = software_id
                db_tag.name = name
                db_tag.font_color = font_color
                db_tag.background_color = background_color
            else:
                db_tag = Tag(id=uuid.uuid4(), software_id=software_id, name=name, font_color=font_color, background_color=background_color)
                session.add(db_tag)
            session.commit()
            # return db_tag
            return session.query(Tag).where(Tag.id == id).one_or_none()
