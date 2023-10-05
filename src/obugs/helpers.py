import uuid
from datetime import datetime, timedelta

from jose import jwt, JWTError


def create_jwt_token(key: str, user_id: uuid.UUID):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=60),
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    return token


def check_user(context):
    authorization_header = context["request"].headers.get("Authorization")
    if authorization_header and authorization_header.startswith("Bearer "):
        token = authorization_header.split("Bearer ")[1]

        try:
            payload = jwt.decode(token, context["config"]['Flask']['JWT_SECRET_KEY'], algorithms="HS256")
            user_id = payload.get("sub")
            return user_id
        except JWTError:
            return None
    return None
