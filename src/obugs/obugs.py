import configparser
import os
import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader

from obugs.database.database import Database
from obugs.database.user import User
from obugs.helpers import create_jwt_token, create_oauth_state, check_oauth_state
from obugs.graphql.schema import schema


class RegisterInfo(BaseModel):
    username: str
    password: str
    email: str
    recaptcha: str


class LoginInfo(BaseModel):
    username: str
    password: str
    recaptcha: str


app = FastAPI()

# Config
config = configparser.ConfigParser()
config.read(Path(os.path.dirname(__file__)) / ".." / "obugs.ini")

# Database
database = Database(uri=config['Flask']['DATABASE'], check_migrations=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4200", "https://obugs.the-cluster.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# GraphQL
async def get_context():
    return {
        "config": config,
        "session_factory": database.session_factory,
        "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=database.session_factory()),
    }


graphql_app = GraphQLRouter(
    schema,
    graphiql=config['Flask'].getboolean('DEBUG'),
    context_getter=get_context,
)
app.include_router(graphql_app, prefix="/graphql")


# Github OAUTH
@app.get('/oauth/github/start')
async def oauth_github_start(request: Request):
    jwt = create_oauth_state(config['Flask']['JWT_SECRET_KEY'])
    github_oauth_url = (f"https://github.com/login/oauth/authorize?"
                        f"client_id={config['Flask']['GITHUB_CLIENT']}&"
                        f"redirect_uri={config['Flask']['OBUGS_BACKEND']}/oauth/github/callback&"
                        f"state={jwt}")
    return RedirectResponse(url=github_oauth_url)


@app.get('/oauth/github/callback')
async def oauth_github_callback(request: Request):
    received_state = request.query_params.get('state')
    github_code = request.query_params.get('code')

    if not check_oauth_state(config['Flask']['JWT_SECRET_KEY'], received_state):
        error = quote("Error with the OAuth state verification, try again.", safe='')
        return RedirectResponse(url=f"{config['Flask']['OBUGS_FRONTEND']}/login?error={error}")

    # ACCESS TOKEN
    github_token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": config['Flask']['GITHUB_CLIENT'],
        "client_secret": config['Flask']['GITHUB_SECRET'],
        "code": github_code,
        "redirect_uri": f"{config['Flask']['OBUGS_BACKEND']}/oauth/github/callback"
    }
    response = requests.post(github_token_url, data=payload, headers={"Accept": "application/json"})
    if response.status_code != 200:
        error = quote("GitHub OAuth token exchange failed, try again.", safe='')
        return RedirectResponse(url=f"{config['Flask']['OBUGS_FRONTEND']}/login?error={error}")
    access_token = response.json()["access_token"]

    # USER INFO
    github_user_url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(github_user_url, headers=headers)
    if response.status_code != 200:
        error = quote("Failed to retrieve user information from GitHub, try again.", safe='')
        return RedirectResponse(url=f"{config['Flask']['OBUGS_FRONTEND']}/login?error={error}")

    user_info = response.json()
    github_id = user_info["id"]
    github_name = user_info["login"]

    # JWT RESULT
    with Session(database.engine) as session:
        user = session.query(User).filter(User.github_id == github_id).first()
        if not user:
            user = User(id=uuid.uuid4(), github_id=github_id, github_name=github_name, is_admin=False,
                        is_banned=False, username=f"{github_name}#Github")
            session.add(user)
            session.commit()
        else:
            user.github_name = github_name
            user.username = f"{github_name}#Github"
            session.commit()

        if user.is_banned:
            error = quote("This user is banned.", safe='')
            return RedirectResponse(url=f"{config['Flask']['OBUGS_FRONTEND']}/login?error={error}")

    jwt = create_jwt_token(config['Flask']['JWT_SECRET_KEY'], user.id)
    escaped_jwt = quote(jwt, safe='')
    return RedirectResponse(url=f"{config['Flask']['OBUGS_FRONTEND']}/login?jwt={escaped_jwt}")
