import strawberry

from obugs.graphql.types.entry import Entry
from obugs.graphql.types.entry_vote import EntryVote


@strawberry.type
class EntryVoteResult:
    entry: Entry
    vote: EntryVote
