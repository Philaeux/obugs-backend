import strawberry

from obugs.graphql.mutations.entry import MutationEntry
from obugs.graphql.mutations.entry_message import MutationEntryMessage
from obugs.graphql.mutations.software import MutationSoftware
from obugs.graphql.mutations.tag import MutationTag
from obugs.graphql.mutations.user import MutationUser
from obugs.graphql.mutations.vote import MutationVote

from obugs.graphql.queries.entry import QueryEntry
from obugs.graphql.queries.entry_message import QueryEntryMessage
from obugs.graphql.queries.software import QuerySoftware
from obugs.graphql.queries.tag import QueryTag
from obugs.graphql.queries.user import QueryUser
from obugs.graphql.queries.vote import QueryVote


@strawberry.type
class Mutation(MutationEntry, MutationEntryMessage, MutationSoftware, MutationTag, MutationUser, MutationVote):
    pass


@strawberry.type
class Query(QueryEntry, QueryEntryMessage, QuerySoftware, QueryTag, QueryUser, QueryVote):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
