import uuid
from datetime import datetime, timedelta

from jose import jwt, JWTError


def create_oauth_state(key: str):
    """Create a Timestamp-Signed-JWT to check there is no tampering with OAUTH process."""
    payload = {
        "timestamp": int(datetime.utcnow().timestamp())
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    return token


def check_oauth_state(key: str, state: str):
    """Check that the Timestamp-Signed-JWT is valid (signed with a recent timestamp)."""
    try:
        decode = jwt.decode(state, key, algorithms="HS256")
        if "timestamp" not in decode:
            return False
        issued_at = datetime.fromtimestamp(decode["timestamp"])
        if datetime.utcnow() - issued_at < timedelta(minutes=2):
            return True
        else:
            return False
    except JWTError:
        return False


def create_jwt_token(key: str, user_id: uuid.UUID):
    """Create a login JWT containing the user id."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=60),
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    return token


def check_user(context):
    """Check headers for a login JWT and return the user_id if valid."""
    authorization_header = context["request"].headers.get("Authorization")
    if authorization_header and authorization_header.startswith("Bearer "):
        token = authorization_header.split("Bearer ")[1]

        try:
            payload = jwt.decode(token, context["config"]['Default']['JWT_SECRET_KEY'], algorithms="HS256")
            user_id = payload.get("sub")
            return user_id
        except JWTError:
            return None
    return None
