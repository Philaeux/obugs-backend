from typing import Any
from flask import Request, Response
from strawberry.flask.views import GraphQLView


class MyGraphQLView(GraphQLView):
    init_every_request = False
    config = None
    engine = None

    def get_context(self, request: Request, response: Response) -> Any:
        return {"config": MyGraphQLView.config, "engine": MyGraphQLView.engine}
