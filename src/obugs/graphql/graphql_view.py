from typing import Any
from flask import Request, Response
from strawberry.flask.views import AsyncGraphQLView
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader


class MyGraphQLView(AsyncGraphQLView):
    init_every_request = False
    config = None
    session_factory = None

    async def get_context(self, request: Request, response: Response) -> Any:
        return {
            "config": MyGraphQLView.config,
            "session_factory": MyGraphQLView.session_factory,
            "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=MyGraphQLView.session_factory()),
        }
