import datetime
from typing import Optional

import strawberry
from sqlalchemy.orm.session import Session
from sqlalchemy import select
from flask_jwt_extended import jwt_required, get_jwt_identity

from obugs.data.database.database import Database
from obugs.data.database.entity_software import SoftwareEntity
from obugs.data.database.entity_tag import TagEntity
from obugs.data.database.entity_user import UserEntity
from obugs.data.database.entity_entry import EntryEntity
from obugs.data.database.entity_entry_vote import EntryVoteEntity
from obugs.data.database.entity_entry_message import EntryMessageEntity, EntryMessageCreationEntity, EntryMessageCommentEntity, EntryMessagePetitionEntity


@strawberry.type
class User:
    id: int
    username: str

    @staticmethod
    def sqla(entity: UserEntity) -> Optional["User"]:
        if entity is None:
            return None
        return User(
            id=entity.id,
            username=entity.username
        )


@strawberry.type()
class Software:
    id: str
    full_name: str
    editor: str
    description: str

    @staticmethod
    def sqla(entity: SoftwareEntity) -> Optional["Software"]:
        if entity is None:
            return None
        return Software(
            id=entity.id,
            full_name=entity.full_name,
            editor=entity.editor,
            description=entity.description
        )


@strawberry.type
class Tag:
    id: int
    name: str
    software_id: str
    font_color: str
    background_color: str

    @staticmethod
    def sqla(entity: TagEntity) -> Optional["Tag"]:
        if entity is None:
            return None
        return Tag(
            id=entity.id,
            name=entity.name,
            software_id=entity.software_id,
            font_color=entity.font_color,
            background_color=entity.background_color
        )


@strawberry.type
class Entry:
    id: int
    software_id: str
    title: str
    tags: list[Tag]
    description: str
    illustration: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str
    rating_total: int
    rating_count: int

    @staticmethod
    def sqla(entity: EntryEntity) -> Optional["Entry"]:
        if entity is None:
            return None
        return Entry(
            id=entity.id,
            software_id=entity.software_id,
            title=entity.title,
            tags=[Tag.sqla(tag) for tag in entity.tags],
            description=entity.description,
            illustration=entity.illustration,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            status=entity.status.name,
            rating_total=entity.rating_total,
            rating_count=entity.rating_count
        )


@strawberry.type
class EntryVote:
    id: int
    entry_id: int
    user_id: str
    rating: int

    @staticmethod
    def sqla(entity: EntryVoteEntity) -> Optional["EntryVote"]:
        if entity is None:
            return None
        return EntryVote(
            id=entity.id,
            entry_id=entity.entry_id,
            user_id=entity.user_id,
            rating=entity.rating
        )

@strawberry.type
class EntryMessage:
    id: int
    entry_id: int
    user_id: int
    created_at: datetime.datetime
    type: str
    state_before: str | None
    state_after: str | None
    rating: int | None
    rating_count: int | None

    @staticmethod
    def sqla(entity: EntryMessageEntity) -> Optional["EntryMessage"]:
        if entity is None:
            return None
        return EntryMessage(
            id=entity.id,
            entry_id=entity.entry_id,
            user_id=entity.user_id,
            created_at=entity.created_at,
            type=entity.type,
            state_before=None,
            state_after=None,
            rating=None,
            rating_count=None
        )


@strawberry.type
class EntryVoteResult:
    entry: Entry
    vote: EntryVote


# noinspection PyArgumentList
@strawberry.type
class Query:

    @strawberry.field
    @jwt_required()
    def current_user(self) -> User | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            sql = select(UserEntity).where(UserEntity.id == current_user['id'])
            db_user = session.scalar(sql)
            return User.sqla(db_user)

    @strawberry.field
    @jwt_required()
    def my_vote(self, entry_id: int) -> EntryVote | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            sql = select(EntryVoteEntity).where(EntryVoteEntity.user_id == current_user['id'], EntryVoteEntity.entry_id == entry_id)
            db_vote = session.scalar(sql)
            return EntryVote.sqla(db_vote)

    @strawberry.field
    def softwares(self) -> list[Software]:
        with Session(Database().engine) as session:
            sql = select(SoftwareEntity).order_by(SoftwareEntity.full_name)
            db_software = session.execute(sql).scalars().all()
            return [Software.sqla(software) for software in db_software]

    @strawberry.field
    def software(self, id: str) -> Software | None:
        with Session(Database().engine) as session:
            sql = select(SoftwareEntity).where(SoftwareEntity.id == id)
            db_software = session.scalar(sql)
            return Software.sqla(db_software)

    @strawberry.field
    def tags(self, software_id: str) -> list[Tag]:
        with Session(Database().engine) as session:
            sql = select(TagEntity).where(TagEntity.software_id == software_id).order_by(TagEntity.name)
            db_tag = session.execute(sql).scalars().all()
            return [Tag.sqla(tag) for tag in db_tag]

    @strawberry.field
    def entry(self, entry_id: int) -> Entry:
        with Session(Database().engine) as session:
            sql = select(EntryEntity).where(EntryEntity.id == entry_id)
            db_entry = session.scalar(sql)
            return Entry.sqla(db_entry)

    @strawberry.field
    def entry_messages(self, entry_id: int) -> list[EntryMessage]:
        with Session(Database().engine) as session:
            sql = select(EntryMessageEntity).where(EntryMessageEntity.entry_id == entry_id)
            db_messages = session.execute(sql).scalars().all()
        return [EntryMessage.sqla(message) for message in db_messages]

    @strawberry.field
    def entries(self, software_id: str, limit: int = 20) -> list[Entry]:
        with Session(Database().engine) as session:
            sql = select(EntryEntity).where(EntryEntity.software_id == software_id).order_by(EntryEntity.updated_at.desc()).limit(limit)
            db_entries = session.execute(sql).scalars().all()
            return [Entry.sqla(entry) for entry in db_entries]


@strawberry.type
class Mutation:

    @strawberry.mutation
    @jwt_required()
    def create_entry(self, software_id: str, title: str, tags: list[str], description: str, illustration: str) -> Entry:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            entry = EntryEntity(software_id=software_id, title=title, description=description, illustration=illustration)
            for tag in tags:
                tag_entity = session.query(TagEntity).where(TagEntity.software_id == software_id, TagEntity.name == tag).one_or_none()
                if tag_entity is not None:
                    entry.tags.append(tag_entity)
            session.add(entry)
            vote = EntryVoteEntity(user_id=current_user['id'], entry=entry, rating=2)
            message = EntryMessageCreationEntity(entry=entry, user_id=current_user['id'], state_after="{'hello': 'world'}")
            session.add(vote)
            session.add(message)
            session.commit()
            return Entry.sqla(entry)

    @strawberry.mutation
    @jwt_required()
    def vote_on_entry(self, entry_id: int, rating: int) -> EntryVoteResult | None:
        current_user = get_jwt_identity()
        with Session(Database().engine) as session:
            sql = select(EntryEntity).where(EntryEntity.id == entry_id)
            db_entry = session.scalar(sql)
            if db_entry is None:
                return None
            sanitize_rating = min(5, max(1, rating))

            sql = select(EntryVoteEntity).where(EntryVoteEntity.user_id == current_user['id'], EntryVoteEntity.entry_id == entry_id)
            db_vote = session.scalar(sql)
            if db_vote is None:
                db_vote = EntryVoteEntity(user_id=current_user['id'], entry_id=entry_id, rating=sanitize_rating)
                session.add(db_vote)
                db_entry.rating_count = db_entry.rating_count + 1
            else:
                db_entry.rating_total = db_entry.rating_total - db_vote.rating
            db_vote.rating = sanitize_rating
            db_entry.rating_total = db_entry.rating_total + sanitize_rating
            session.commit()
            return EntryVoteResult(entry=Entry.sqla(db_entry), vote=EntryVote.sqla(db_vote))


schema = strawberry.Schema(query=Query, mutation=Mutation)
