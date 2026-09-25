def register(client, username="khoa", password="supersecret123"):
    return client.post("/register", data={"username": username, "password": password})


def login(client, username="khoa", password="supersecret123"):
    return client.post("/login", data={"username": username, "password": password})


def test_register_then_redirected_to_collection(client):
    resp = register(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/collection")


def test_register_with_short_password_shows_errors(client):
    resp = register(client, password="short")
    assert resp.status_code == 200
    assert b"at least" in resp.data


def test_login_with_correct_credentials_succeeds(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 302


def test_login_with_wrong_password_fails(client):
    register(client)
    resp = login(client, password="wrongpassword")
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data


def test_collection_requires_login_redirects(client):
    resp = client.get("/collection")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_collection_accessible_after_login(client):
    register(client)
    resp = client.get("/collection", follow_redirects=True)
    assert resp.status_code == 200
    assert b"My Collection" in resp.data


def test_toggle_favorite_requires_login(client):
    resp = client.post("/cards/OP17-080/favorite")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_toggle_favorite_add_and_remove(client):
    register(client)
    resp = client.post("/cards/OP17-080/favorite", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Usopp" in resp.data

    resp = client.get("/collection")
    assert b"Usopp" in resp.data

    # toggling again removes it
    client.post("/cards/OP17-080/favorite")
    resp = client.get("/collection")
    assert b"Usopp" not in resp.data


def test_toggle_favorite_unknown_card_404(client):
    register(client)
    resp = client.post("/cards/NOPE-000/favorite")
    assert resp.status_code == 404


def test_logout_clears_session(client):
    register(client)
    client.post("/logout")
    resp = client.get("/collection")
    assert resp.status_code == 302


def test_login_page_get_renders_form(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Log in" in resp.data


def test_register_page_get_renders_form(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create an account" in resp.data
