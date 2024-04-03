import base64
import uuid
from contextlib import asynccontextmanager
from urllib.parse import quote

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader

from obugs.database.database import Database
from obugs.database.user import User
from obugs.graphql.schema import schema
from obugs.settings import Settings
from obugs.utils.helpers import create_jwt_token, create_oauth_state, check_oauth_state

# App
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Add startup functions here
    yield
    # Add shutdown functions here

app = FastAPI(lifespan=lifespan)

# Database
database = Database(uri=settings.database_uri, check_migrations=True)

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
        "settings": settings,
        "session_factory": database.session_factory,
        "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=database.session_factory()),
    }


graphql_app = GraphQLRouter(
    schema,
    graphiql=settings.debug,
    context_getter=get_context,
)
app.include_router(graphql_app, prefix="/graphql")


@app.get('/oauth/github/start')
async def oauth_github_start():
    """Start the GitHub OAUTH process. Prepare a state to check cross call then redirect."""
    jwt = create_oauth_state(settings.jwt_secret_key)
    github_oauth_url = (f"https://github.com/login/oauth/authorize?"
                        f"client_id={settings.github_client}&"
                        f"redirect_uri={settings.backend_uri}/oauth/github/callback&"
                        f"state={jwt}")
    return RedirectResponse(url=github_oauth_url)


@app.get('/oauth/github/callback')
async def oauth_github_callback(request: Request):
    """Callback of the GitHub OAUTH. Check code and state, log the user, then redirect to frontend."""
    state = request.query_params.get('state')
    code = request.query_params.get('code')

    if not check_oauth_state(settings.jwt_secret_key, state):
        error = quote("Error with the OAuth state verification, try again.", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

    # ACCESS TOKEN
    github_token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": settings.github_client,
        "client_secret": settings.github_secret,
        "code": code,
        "redirect_uri": f"{settings.backend_uri}/oauth/github/callback"
    }
    response = requests.post(github_token_url, data=payload, headers={"Accept": "application/json"})
    if response.status_code != 200:
        error = quote("GitHub OAuth token exchange failed, try again.", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")
    access_token = response.json()["access_token"]

    # USER INFO
    github_user_url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(github_user_url, headers=headers)
    if response.status_code != 200:
        error = quote("Failed to retrieve user information from GitHub, try again.", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

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
            return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

    jwt = create_jwt_token(settings.jwt_secret_key, user.id)
    escaped_jwt = quote(jwt, safe='')
    return RedirectResponse(url=f"{settings.frontend_uri}/login?jwt={escaped_jwt}")


@app.get('/oauth/reddit/start')
async def oauth_reddit_start():
    """Start the Reddit OAUTH process. Prepare a state to check cross call then redirect."""
    jwt = create_oauth_state(settings.jwt_secret_key)
    reddit_oauth_url = (f"https://www.reddit.com/api/v1/authorize?response_type=code&duration=temporary&"
                        f"client_id={settings.reddit_client}&"
                        f"redirect_uri={settings.backend_uri}/oauth/reddit/callback&"
                        f"state={jwt}&"
                        f"scope=identity")
    return RedirectResponse(url=reddit_oauth_url)


@app.get('/oauth/reddit/callback')
async def oauth_reddit_callback(request: Request):
    """Callback of the Reddit OAUTH. Check code and state, log the user, then redirect to frontend."""
    error = request.query_params.get('error')
    state = request.query_params.get('state')
    code = request.query_params.get('code')

    if error is not None:
        error = quote(f"Error login with Reddit: '{error}'", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

    if not check_oauth_state(settings.jwt_secret_key, state):
        error = quote("Error with the OAuth state verification, try again.", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

    # ACCESS TOKEN
    reddit_token_url = "https://www.reddit.com/api/v1/access_token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{settings.backend_uri}/oauth/reddit/callback"
    }
    credentials = f"{settings.reddit_client}:{settings.reddit_secret}".encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + base64.b64encode(credentials).decode("utf-8"),
        'User-Agent': 'oBugs/1.0 (by /u/philaeux)'
    }
    response = requests.post(reddit_token_url, data=payload, headers=headers)
    if response.status_code != 200:
        error = quote("Reddit OAuth token exchange failed, try again.", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")
    access_token = response.json()["access_token"]

    # USER INFO
    reddit_user_url = "https://oauth.reddit.com/api/v1/me"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        'User-Agent': 'oBugs/1.0 (by /u/philaeux)'
    }
    response = requests.get(reddit_user_url, headers=headers)
    if response.status_code != 200:
        error = quote("Failed to retrieve user information from Reddit, try again.", safe='')
        return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

    user_info = response.json()
    reddit_id = user_info["id"]
    reddit_name = user_info["name"]

    # Revoke access token
    payload = {
        "token": access_token,
        "token_type_hint": access_token
    }
    requests.post("https://www.reddit.com/api/v1/revoke_token", data=payload, headers=headers)

    # JWT RESULT
    with Session(database.engine) as session:
        user = session.query(User).filter(User.reddit_id == reddit_id).first()
        if not user:
            user = User(id=uuid.uuid4(), reddit_id=reddit_id, reddit_name=reddit_name, is_admin=False,
                        is_banned=False, username=f"{reddit_name}#Reddit")
            session.add(user)
            session.commit()
        else:
            user.reddit_name = reddit_name
            user.username = f"{reddit_name}#Github"
            session.commit()

        if user.is_banned:
            error = quote("This user is banned.", safe='')
            return RedirectResponse(url=f"{settings.frontend_uri}/login?error={error}")

    jwt = create_jwt_token(settings.jwt_secret_key, user.id)
    escaped_jwt = quote(jwt, safe='')
    return RedirectResponse(url=f"{settings.frontend_uri}/login?jwt={escaped_jwt}")
