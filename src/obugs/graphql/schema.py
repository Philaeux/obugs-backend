import strawberry

from obugs.graphql.mutations.mutations import MutationAll
from obugs.graphql.mutations.entry_message import MutationEntryMessage
from obugs.graphql.mutations.software import MutationSoftware
from obugs.graphql.mutations.tag import MutationTag
from obugs.graphql.queries import Query


@strawberry.type
class Mutation(MutationAll, MutationEntryMessage, MutationSoftware, MutationTag):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
