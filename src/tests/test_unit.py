import uuid

from obugs.utils.helpers import create_oauth_state, check_oauth_state, create_jwt_token, check_user


def test_oauth_state_gen():
    state = create_oauth_state("TEST_KEY")
    assert check_oauth_state("TEST_KEY", state)
    assert not check_oauth_state("WRONG_KEY", state)


def test_user_token():
    user_uuid = uuid.uuid4()
    token = create_jwt_token("TEST_KEY", user_uuid)

    decoded = check_user("TEST_KEY", None)
    assert decoded is None
    decoded = check_user("TEST_KEY", "wrong  header")
    assert decoded is None
    decoded = check_user("TEST_KEY", f"Bearer {token}")
    assert str(decoded) == str(user_uuid)
    decoded = check_user("TEST_KEY", f"Bearer {token}XX")
    assert decoded is None
