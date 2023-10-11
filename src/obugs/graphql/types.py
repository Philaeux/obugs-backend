import strawberry
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper

from obugs.database.entry import Entry as EntryEntity
from obugs.database.entry_message import (EntryMessage as EntryMessageEntity,
                                          EntryMessageCreation as EntryMessageCreationEntity,
                                          EntryMessageComment as EntryMessageCommentEntity,
                                          EntryMessagePatch as EntryMessagePatchEntity)
from obugs.database.software import Software as SoftwareEntity
from obugs.database.software_suggestion import SoftwareSuggestion as SoftwareSuggestionEntity
from obugs.database.tag import Tag as TagEntity
from obugs.database.user import User as UserEntity
from obugs.database.user_software_role import UserSoftwareRole as UserSoftwareRole
from obugs.database.vote import Vote as VoteEntity


# ORM MAPPING
strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()


@strawberry_sqlalchemy_mapper.type(EntryEntity)
class Entry:
    pass


@strawberry_sqlalchemy_mapper.interface(EntryMessageEntity)
class EntryMessage:
    pass


@strawberry_sqlalchemy_mapper.type(EntryMessageCreationEntity)
class EntryMessageCreation:
    pass


@strawberry_sqlalchemy_mapper.type(EntryMessageCommentEntity)
class EntryMessageComment:
    pass


@strawberry_sqlalchemy_mapper.type(EntryMessagePatchEntity)
class EntryMessagePatch:
    pass


@strawberry_sqlalchemy_mapper.type(SoftwareEntity)
class Software:
    __exclude__ = ["entries"]


@strawberry_sqlalchemy_mapper.type(SoftwareSuggestionEntity)
class SoftwareSuggestion:
    pass


@strawberry_sqlalchemy_mapper.type(TagEntity)
class Tag:
    __exclude__ = ["entries"]


@strawberry_sqlalchemy_mapper.type(UserEntity)
class User:
    __exclude__ = ["password", "email", "is_activated", "activation_token"]


@strawberry_sqlalchemy_mapper.type(UserSoftwareRole)
class UserSoftwareRole:
    pass


@strawberry_sqlalchemy_mapper.type(VoteEntity)
class Vote:
    __exclude__ = ["votes"]


# COMPOSITE TYPES
@strawberry.type
class OperationDone:
    success: bool


@strawberry.type
class ProcessPatchSuccess:
    entry: Entry
    entry_message: EntryMessagePatch


@strawberry.type
class VoteUpdate:
    rating_total: int
    rating_count: int


# OTHERS
@strawberry.type
class OBugsError:
    message: str
