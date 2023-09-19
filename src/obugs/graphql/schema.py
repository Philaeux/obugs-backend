import strawberry

from obugs.graphql.mutations import Mutation
from obugs.graphql.queries import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
