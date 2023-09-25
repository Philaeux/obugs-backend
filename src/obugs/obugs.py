import configparser
import os
import requests
import string
from pathlib import Path
from secrets import choice

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_mail import Mail, Message
from sqlalchemy.orm import Session
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from werkzeug.security import generate_password_hash, check_password_hash

from obugs.graphql.graphql_view import MyGraphQLView
from obugs.graphql.schema import schema
from obugs.database.database import Database
from obugs.database.entity_user import UserEntity


class Obugs:

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)

        self.config = configparser.ConfigParser()
        self.config.read(Path(os.path.dirname(__file__)) / ".." / "obugs.ini")
        self.app.config['DEBUG'] = self.config['Flask'].getboolean('DEBUG')
        self.app.config["JWT_SECRET_KEY"] = self.config['Flask']['JWT_SECRET_KEY']
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 1296000
        self.app.config['MAIL_SERVER'] = self.config['Flask']['MAIL_SERVER']
        self.app.config['MAIL_PORT'] = 587  # Port for the email server
        self.app.config['MAIL_USE_TLS'] = True  # Use TLS (True/False)
        self.app.config['MAIL_USE_SSL'] = False  # Use SSL (True/False)
        self.app.config['MAIL_USERNAME'] = self.config['Flask']['MAIL_USERNAME']
        self.app.config['MAIL_PASSWORD'] = self.config['Flask']['MAIL_PASSWORD']
        self.app.config['MAIL_DEFAULT_SENDER'] = self.config['Flask']['MAIL_DEFAULT_SENDER']
        self.app.config['RECAPTCHA'] = self.config['Flask']['RECAPTCHA']

        self.database = Database(uri=self.config['Flask']['DATABASE'], check_migrations=True)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = self.database.uri
        self.mail = Mail(self.app)
        self.jwt = JWTManager(self.app)

        # Routes
        MyGraphQLView.config = self.config
        self.app.add_url_rule(
            "/graphql",
            view_func=MyGraphQLView.as_view("graphql_view", schema=schema)
        )

        @self.app.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            username = data.get('username', '')
            password = data.get('password', '')
            email = data.get('email', '')
            recaptcha = data.get('recaptcha', '')

            if len(username) < 3 or len(password) < 6 or len(email) < 3:
                return jsonify({'error': 'Username or password or email invalid.', 'message': ''})

            try:
                response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                    'secret': self.config['Flask']['RECAPTCHA'],
                    'response': recaptcha
                })
                result = response.json()
                if not result['success']:
                    return jsonify({'error': 'Invalid recaptcha.', 'message': ''})
            except Exception:
                return jsonify({'error': 'Error with recaptcha check.', 'message': ''})

            with Session(self.database.engine) as session:
                if session.query(UserEntity).filter(UserEntity.username == username).first():
                    return jsonify({'error': 'Username already used.', 'message': ''}), 200
                if session.query(UserEntity).filter(UserEntity.email == email).first():
                    return jsonify({'error': 'Email already used.', 'message': ''}), 200

                new_user = UserEntity(
                    username=username,
                    password=generate_password_hash(password, method='scrypt'),
                    email=email,
                    activation_token=''.join(choice(string.ascii_letters + string.digits) for _ in range(32)),
                    is_admin=False,
                    is_banned=False,
                    is_activated=True
                )
                if username == 'Philaeux':
                    new_user.is_admin = True

                # activation_link = (f"{self.config['Flask']['OBUGS_FRONTEND']}/login?"
                #                    f"username={username}&token={new_user.activation_token}")
                # message = Message(subject="Obugs Activation Link",
                #                   recipients=[email],
                #                   body=f"To confirm your registration, use this link {activation_link}")
                # self.mail.send(message)
                session.add(new_user)
                session.commit()

            return jsonify(
                {'error': '',
                 'message': 'User registered successfully. You can login.'}), 200

        @self.app.route('/activate', methods=['POST'])
        def activate():
            data = request.get_json()
            username = data.get('username', '')
            token = data.get('token', '')

            if len(username) < 3 or len(token) != 32:
                return jsonify({'error': 'Invalid user or activate token.', 'message': ''}), 200

            with Session(self.database.engine) as session:
                user = session.query(UserEntity).filter(UserEntity.username == username).first()
                if not user or user.activation_token != token:
                    return jsonify({'error': 'Invalid or activate token.', 'message': ''}), 200
                user.is_activated = True
                session.commit()
            return jsonify({'error': '', 'message': 'Account successfully activated. You can now login.'}), 200

        @self.app.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            with Session(self.database.engine) as session:
                user = session.query(UserEntity).filter(UserEntity.username == username).first()

                if not user or not check_password_hash(user.password, password):
                    return jsonify({'error': 'Invalid username or password.', 'message': ''}), 200

                if user.is_banned:
                    return jsonify({'error': 'This user is banned.', 'message': ''}), 200

                access_token = create_access_token(identity={"id": user.id})
            return jsonify({'error': '', 'message': access_token}), 200

    def run(self):
        if self.app.config['DEBUG']:
            self.app.run()
        else:
            http_server = HTTPServer(WSGIContainer(self.app))
            http_server.listen(5000)
            IOLoop.instance().start()
