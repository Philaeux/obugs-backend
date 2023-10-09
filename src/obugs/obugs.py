import configparser
import os
from pathlib import Path
from secrets import choice
import string

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader
from werkzeug.security import generate_password_hash, check_password_hash

from obugs.database.database import Database
from obugs.database.user import User
from obugs.helpers import create_jwt_token
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


class Obugs:
    def __init__(self, app):
        self.app = app

        # Config
        self.config = configparser.ConfigParser()
        self.config.read(Path(os.path.dirname(__file__)) / ".." / "obugs.ini")

        # Database
        self.database = Database(uri=self.config['Flask']['DATABASE'], check_migrations=True)

        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:4200", "https://obugs.the-cluster.org"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

        # MAIL
        # self.app.config['MAIL_SERVER'] = self.config['Flask']['MAIL_SERVER']
        # self.app.config['MAIL_PORT'] = 587  # Port for the email server
        # self.app.config['MAIL_USE_TLS'] = True  # Use TLS (True/False)
        # self.app.config['MAIL_USE_SSL'] = False  # Use SSL (True/False)
        # self.app.config['MAIL_USERNAME'] = self.config['Flask']['MAIL_USERNAME']
        # self.app.config['MAIL_PASSWORD'] = self.config['Flask']['MAIL_PASSWORD']
        # self.app.config['MAIL_DEFAULT_SENDER'] = self.config['Flask']['MAIL_DEFAULT_SENDER']
        # self.mail = Mail(self.app)

        # GraphQL
        async def get_context():
            return {
                "config": self.config,
                "session_factory": self.database.session_factory,
                "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=self.database.session_factory()),
            }

        self.graphql_app = GraphQLRouter(
            schema,
            graphiql=self.config['Flask'].getboolean('DEBUG'),
            context_getter=get_context,
        )
        self.app.include_router(self.graphql_app, prefix="/graphql")

        # Register/Login/Activate routes

        @self.app.post('/register')
        async def register(register_info: RegisterInfo):
            if len(register_info.username) < 3 or len(register_info.password) < 6 or len(register_info.email) < 3:
                return {'error': 'Username or password or email invalid.', 'message': ''}

            try:
                response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                    'secret': self.config['Flask']['RECAPTCHA'],
                    'response': register_info.recaptcha
                })
                result = response.json()
                if not result['success']:
                    return {'error': 'Invalid recaptcha.', 'message': ''}
            except Exception:
                return {'error': 'Error with recaptcha check.', 'message': ''}

            with Session(self.database.engine) as session:
                if session.query(User).filter(User.username == register_info.username).first():
                    return {'error': 'Username already used.', 'message': ''}
                if session.query(User).filter(User.email == register_info.email).first():
                    return {'error': 'Email already used.', 'message': ''}

                new_user = User(
                    username=register_info.username,
                    password=generate_password_hash(register_info.password, method='scrypt'),
                    email=register_info.email,
                    activation_token=''.join(choice(string.ascii_letters + string.digits) for _ in range(32)),
                    is_admin=False,
                    is_banned=False,
                    is_activated=True
                )

                # activation_link = (f"{self.config['Flask']['OBUGS_FRONTEND']}/login?"
                #                    f"username={username}&token={new_user.activation_token}")
                # message = Message(subject="Obugs Activation Link",
                #                   recipients=[email],
                #                   body=f"To confirm your registration, use this link {activation_link}")
                # self.mail.send(message)
                session.add(new_user)
                session.commit()

            return {'error': '', 'message': 'User registered successfully. You can login.'}

        @self.app.post('/login')
        async def login(login_info: LoginInfo):
            try:
                response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                    'secret': self.config['Flask']['RECAPTCHA'],
                    'response': login_info.recaptcha
                })
                result = response.json()
                if not result['success']:
                    return {'error': 'Invalid recaptcha.', 'message': ''}
            except Exception:
                return {'error': 'Error with recaptcha check.', 'message': ''}

            with Session(self.database.engine) as session:
                user = session.query(User).filter(User.username == login_info.username).first()
                if not user or not check_password_hash(user.password, login_info.password):
                    return {'error': 'Invalid username or password.', 'message': ''}
                if user.is_banned:
                    return {'error': 'This user is banned.', 'message': ''}

            return {'error': '', 'message': create_jwt_token(self.config['Flask']['JWT_SECRET_KEY'], user.id)}

        # @self.app.route('/activate', methods=['POST'])
        # def activate():
        #     data = request.get_json()
        #     username = data.get('username', '')
        #     token = data.get('token', '')
        #
        #     if len(username) < 3 or len(token) != 32:
        #         return jsonify({'error': 'Invalid user or activate token.', 'message': ''}), 200
        #
        #     with Session(self.database.engine) as session:
        #         user = session.query(User).filter(User.username == username).first()
        #         if not user or user.activation_token != token:
        #             return jsonify({'error': 'Invalid or activate token.', 'message': ''}), 200
        #         user.is_activated = True
        #         session.commit()
        #     return jsonify({'error': '', 'message': 'Account successfully activated. You can now login.'}), 200
