import uuid


def test_rest_hello_world(mock_app):
    """Example of a test on the /hello endpoint"""
    response = mock_app.get('/hello')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_debug_user_add_remove(mock_app):
    """Test to create and delete users with the debug endpoint"""
    user_id = uuid.uuid4()
    response = mock_app.post("/debug/user/add", json={"id": str(user_id),
                                                      "github_id": 0,
                                                      "github_name": "TEST",
                                                      "reddit_id": None,
                                                      "reddit_name": None,
                                                      "is_admin": True})
    assert response.status_code == 200
    assert response.json() == {"error": None}

    response = mock_app.post("/debug/user/remove", json={"id": str(uuid.uuid4())})
    assert response.status_code == 200
    assert response.json() == {"error": "No such user in database"}

    response = mock_app.post("/debug/user/remove", json={"id": str(user_id)})
    assert response.status_code == 200
    assert response.json() == {"error": None}

# TODO User Creation Fixture

def test_query_softwares(mock_app):
    """Example of a graphql query softwares"""
    query = """
    {
        softwares(search: null){
            id
        }
    }
    """
    response = mock_app.post("/graphql", json={"query": query})
    assert response.status_code == 200
    json = response.json()
    assert "data" in json
    assert "softwares" in json["data"]
    assert len(json["data"]["softwares"]) == 0
