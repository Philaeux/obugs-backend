import strawberry
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select
from sqlalchemy.orm import Session
import uuid
from uuid import UUID

from obugs.database.database import Database
from obugs.database.entity_entry import EntryEntity
from obugs.database.entity_entry_message import EntryMessageEntity
from obugs.database.entity_vote import VoteEntity
from obugs.database.entity_software import SoftwareEntity
from obugs.database.entity_tag import TagEntity
from obugs.database.entity_user import UserEntity
from obugs.graphql.types.entry import Entry
from obugs.graphql.types.entry_message import EntryMessage
from obugs.graphql.types.software import Software
from obugs.graphql.types.tag import Tag
from obugs.graphql.types.user import User
from obugs.graphql.types.vote import Vote


# noinspection PyArgumentList
@strawberry.type
class Query:

    @strawberry.field
    @jwt_required()
    def current_user(self) -> User | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == UUID(current_user['id'])).one_or_none()
            if db_user is None:
                return None
            else:
                return db_user.gql()

    @strawberry.field
    @jwt_required()
    def my_vote(self, subject_id: uuid.UUID) -> Vote | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            db_vote = session.query(VoteEntity).where(VoteEntity.user_id == UUID(current_user['id']),
                                                      VoteEntity.subject_id == subject_id).one_or_none()
            if db_vote is None:
                return None
            else:
                return db_vote.gql()

    @strawberry.field
    def user(self, user_id: uuid.UUID) -> User | None:
        with Session(Database().engine) as session:
            db_user = session.query(UserEntity).where(UserEntity.id == user_id).one_or_none()
            if db_user is None:
                return None
            else:
                return db_user.gql()

    @strawberry.field
    def software(self, software_id: str) -> Software | None:
        with Session(Database().engine) as session:
            db_software = session.query(SoftwareEntity).where(SoftwareEntity.id == software_id).one_or_none()
            if db_software is None:
                return None
            else:
                return db_software.gql()

    @strawberry.field
    def softwares(self) -> list[Software]:
        with Session(Database().engine) as session:
            sql = select(SoftwareEntity).order_by(SoftwareEntity.full_name)
            db_software = session.execute(sql).scalars().all()
            return [software.gql() for software in db_software]

    @strawberry.field
    def tags(self, software_id: str) -> list[Tag]:
        with Session(Database().engine) as session:
            sql = select(TagEntity).where(TagEntity.software_id == software_id).order_by(TagEntity.name)
            db_tag = session.execute(sql).scalars().all()
            return [tag.gql() for tag in db_tag]

    @strawberry.field
    def entry(self, entry_id: uuid.UUID) -> Entry | None:
        with Session(Database().engine) as session:
            db_entry = session.query(EntryEntity).where(EntryEntity.id == entry_id).one_or_none()
            if db_entry is None:
                return None
            else:
                return db_entry.gql()

    @strawberry.field
    def entries(self, software_id: str, limit: int = 20) -> list[Entry]:
        with (Session(Database().engine) as session):
            sql = select(EntryEntity) \
                .where(EntryEntity.software_id == software_id) \
                .order_by(EntryEntity.updated_at.desc()) \
                .limit(limit)

            db_entries = session.execute(sql).scalars().all()
            return [entry.gql() for entry in db_entries]

    @strawberry.field
    def entry_messages(self, entry_id: uuid.UUID, limit: int = 20) -> list[EntryMessage]:
        with Session(Database().engine) as session:
            sql = select(EntryMessageEntity)\
                .where(EntryMessageEntity.entry_id == entry_id)\
                .order_by(EntryMessageEntity.created_at)\
                .limit(limit)
            db_messages = session.execute(sql).scalars().all()
            return [message.gql() for message in db_messages]
