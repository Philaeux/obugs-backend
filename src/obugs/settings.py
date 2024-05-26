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
        github_client: Login with GitHub app client ID
        github_secret: Login with GitHub app secret
        reddit_client: Login with Reddit app client ID
        reddit_secret: Login with Reddit app secret
    """
    debug: bool = True
    jwt_secret_key: str = "change-me"
    frontend_uri: str = "http://127.0.0.1:4200"
    backend_uri: str = "http://127.0.0.1:5000"
    database_uri: str = "sqlite+pysqlite:///sqlite.db"
    recaptcha: str = "make-an-application"
    github_client: str = "make-an-application"
    github_secret: str = "change-me"
    reddit_client: str = "make-an-application"
    reddit_secret: str = "change-me"

    def load_from_ini(self):
        """Create a default configuration, then read from settings.ini"""
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
