from flask import Flask, request, jsonify
from strawberry.flask.views import GraphQLView
from sqlalchemy.orm import Session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from obugs.data.graphql.schema import schema
from obugs.data.database.database import Database

from obugs.data.database.entity_user import UserEntity


class Obugs:

    def __init__(self):
        self.database = Database()

        self.app = Flask(__name__)
        self.app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
        self.jwt = JWTManager(self.app)
        self.app.add_url_rule(
            "/graphql",
            view_func=GraphQLView.as_view("graphql_view", schema=schema),
        )

        @self.app.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Check if the username already exists
            with Session(self.database.engine) as session:
                if session.query(UserEntity).filter(UserEntity.username == username).first():
                    return jsonify({'message': 'Username already exists'}), 400

                # Hash the password before saving it
                hashed_password = generate_password_hash(password, method='sha256')

                new_user = UserEntity(username=username, password=hashed_password)
                session.add(new_user)
                session.commit()

            return jsonify({'message': 'User registered successfully'}), 201

        @self.app.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            with Session(self.database.engine) as session:
                user = session.query(UserEntity).filter(UserEntity.username == username).first()

                if not user or not check_password_hash(user.password, password):
                    return jsonify({'message': 'Invalid username or password'}), 401

                access_token = create_access_token(identity={"username": username, "id": user.id})
            return jsonify({'access_token': access_token}), 200

    def run(self):
        self.app.run()
