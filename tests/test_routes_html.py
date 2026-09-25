def test_home_page_lists_cards(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Card Database" in resp.data


def test_home_page_search_filters_by_query(client):
    resp = client.get("/?q=shanks")
    assert resp.status_code == 200
    assert b"Shanks" in resp.data


def test_card_detail_page(client):
    resp = client.get("/cards/OP17-080")
    assert resp.status_code == 200
    assert b"Usopp" in resp.data


def test_card_detail_page_404_for_unknown_card(client):
    resp = client.get("/cards/NOPE-000")
    assert resp.status_code == 404


def test_card_art_svg_endpoint(client):
    resp = client.get("/cards/OP17-080/art.svg")
    assert resp.status_code == 200
    assert resp.content_type == "image/svg+xml"


def test_card_art_svg_404_for_unknown_card(client):
    resp = client.get("/cards/NOPE-000/art.svg")
    assert resp.status_code == 404


def test_deck_new_page_lists_leaders(client):
    resp = client.get("/decks/new")
    assert resp.status_code == 200
    assert b"Leader" in resp.data


def test_full_deck_lifecycle_via_html_forms(client):
    resp = client.post("/decks/new", data={"name": "My Red Deck", "leader_code": "OP17-079"})
    assert resp.status_code == 200
    assert b"My Red Deck" in resp.data

    decks = client.get("/api/decks").get_json()
    deck_id = next(d["id"] for d in decks if d["name"] == "My Red Deck")

    resp = client.post(f"/decks/{deck_id}/cards", data={"card_code": "OP17-080", "quantity": 4})
    assert b"Usopp" in resp.data
    assert b"4" in resp.data

    resp = client.post(f"/decks/{deck_id}/cards/OP17-080/remove")
    assert resp.status_code == 200

    resp = client.post(f"/decks/{deck_id}/delete", follow_redirects=True)
    assert resp.status_code == 200

    decks_after = client.get("/api/decks").get_json()
    assert all(d["id"] != deck_id for d in decks_after)


def test_deck_detail_404_for_unknown_deck(client):
    resp = client.get("/decks/does-not-exist")
    assert resp.status_code == 404


def test_card_without_custom_art_still_uses_generated_svg(client):
    resp = client.get("/cards/OP17-080")
    assert resp.status_code == 200
    assert b"/cards/OP17-080/art.svg" in resp.data


def test_ground_death_uses_generated_svg_like_every_other_card(client):
    resp = client.get("/cards/OP14-096")
    assert resp.status_code == 200
    assert b"/cards/OP14-096/art.svg" in resp.data
