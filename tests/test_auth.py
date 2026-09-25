from app.auth import MIN_PASSWORD_LEN, UserStore


def test_register_creates_user_with_hashed_password():
    store = UserStore()
    errors = store.register("khoa", "supersecret123")
    assert errors == []
    user = store.get("khoa")
    assert user is not None
    assert user.password_hash != "supersecret123"  # never stored in plain text


def test_register_rejects_invalid_username():
    store = UserStore()
    errors = store.register("a", "supersecret123")
    assert any("Username" in e for e in errors)


def test_register_rejects_short_password():
    store = UserStore()
    errors = store.register("khoa", "short")
    assert any(f"{MIN_PASSWORD_LEN}" in e for e in errors)


def test_register_rejects_duplicate_username_case_insensitive():
    store = UserStore()
    store.register("khoa", "supersecret123")
    errors = store.register("KHOA", "anotherpassword")
    assert any("already taken" in e for e in errors)


def test_authenticate_succeeds_with_correct_password():
    store = UserStore()
    store.register("khoa", "supersecret123")
    user = store.authenticate("khoa", "supersecret123")
    assert user is not None
    assert user.username == "khoa"


def test_authenticate_fails_with_wrong_password():
    store = UserStore()
    store.register("khoa", "supersecret123")
    assert store.authenticate("khoa", "wrongpassword") is None


def test_authenticate_fails_for_unknown_user():
    store = UserStore()
    assert store.authenticate("ghost", "whatever123") is None


def test_favorites_add_remove_and_deduplicate():
    store = UserStore()
    store.register("khoa", "supersecret123")
    assert store.add_favorite("khoa", "OP17-080") is True
    store.add_favorite("khoa", "OP17-080")  # adding twice should not duplicate
    user = store.get("khoa")
    assert user.favorite_codes == ["OP17-080"]

    assert store.remove_favorite("khoa", "OP17-080") is True
    assert store.get("khoa").favorite_codes == []


def test_favorite_actions_on_unknown_user_return_false():
    store = UserStore()
    assert store.add_favorite("ghost", "OP17-080") is False
    assert store.remove_favorite("ghost", "OP17-080") is False
