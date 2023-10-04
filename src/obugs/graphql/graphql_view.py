from typing import Any
from flask import Request, Response
from strawberry.flask.views import GraphQLView
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader


class MyGraphQLView(GraphQLView):
    init_every_request = False
    config = None
    session_factory = None

    def get_context(self, request: Request, response: Response) -> Any:
        return {
            "config": MyGraphQLView.config,
            "session_factory": MyGraphQLView.session_factory,
            "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=MyGraphQLView.session_factory),
        }
