def test_root_not_found(client):
    response = client.get(path="/")
    assert response.status_code == 404
