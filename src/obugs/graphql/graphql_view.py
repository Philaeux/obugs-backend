
from strawberry.flask.views import GraphQLView


class MyGraphQLView(GraphQLView):
    init_every_request = False
