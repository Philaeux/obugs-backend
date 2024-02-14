import configparser
from pathlib import Path

from obugs.utils.singleton_meta import SingletonMeta


class Settings(metaclass=SingletonMeta):
    """Parameters of the application read from settings.ini
    
    Attributes:
        debug: Flag to set debug options in all application
        jwt_secret_key: secret to generate JWTs
        frontend_uri: URI to the frontend related to this app (to redirect auth)
        backend_uri: URI this backend is accessed from
        database_uri: URI to connect to the database
        recaptcha: Recaptcha secret
        github_client: Login with Github app client ID
        github_secret: Login with Github app secret
        reddit_client: Login with Reddit app client ID
        reddit_secret: Login with Reddit app secret
    """
    debug: bool = True
    jwt_secret_key: str = "sssssssss"
    frontend_uri: str = "http://127.0.0.1:4200"
    backend_uri: str = "http://127.0.0.1:5000"
    database_uri: str = "postgresql+psycopg://obugs:sssssssss@host.docker.internal:5432/obugs"
    recaptcha: str = "sssssssss"
    github_client: str = "sssssssss"
    github_secret: str = "sssssssss"
    reddit_client: str = "sssssssss"
    reddit_secret: str = "sssssssss"

    def __init__(self):
        """Lis le fichier de configuration depuis le fichier settings.ini"""
        cfg = configparser.ConfigParser()
        cfg.read(Path(__file__).parent / ".." / "settings.ini")

        self.debug = cfg['DEFAULT'].getboolean('debug', fallback=self.debug)
        self.jwt_secret_key = cfg['DEFAULT'].get('jwt_secret_key', fallback=self.jwt_secret_key)
        self.frontend_uri = cfg['DEFAULT'].get('frontend_uri', fallback=self.frontend_uri)
        self.backend_uri = cfg['DEFAULT'].get('backend_uri', fallback=self.backend_uri)
        self.database_uri = cfg['DEFAULT'].get('database_uri', fallback=self.database_uri)
        self.recaptcha = cfg['DEFAULT'].get('recaptcha', fallback=self.recaptcha)
        self.github_client = cfg['DEFAULT'].get('github_client', fallback=self.github_client)
        self.github_secret = cfg['DEFAULT'].get('github_secret', fallback=self.github_secret)
        self.reddit_client = cfg['DEFAULT'].get('reddit_client', fallback=self.reddit_client)
        self.reddit_secret = cfg['DEFAULT'].get('reddit_secret', fallback=self.reddit_secret)
