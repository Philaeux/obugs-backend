import strawberry

from obugs.graphql.types.entry import Entry
from obugs.graphql.types.entry_message import EntryMessage


@strawberry.type
class MessageDeleteSuccess:
    success: bool


@strawberry.type
class ProcessPatchSuccess:
    entry: Entry
    entry_message: EntryMessage


@strawberry.type
class VoteUpdate:
    rating_total: int
    rating_count: int
