import strawberry

from obugs.graphql.mutations.mutations import MutationAll
from obugs.graphql.mutations.entry_message import MutationEntryMessage
from obugs.graphql.queries import Query


@strawberry.type
class Mutation(MutationAll, MutationEntryMessage):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
