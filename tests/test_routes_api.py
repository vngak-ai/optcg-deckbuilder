def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_metrics_endpoint_exposes_counters(client):
    client.get("/health")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "optcg_http_requests_total" in body
    assert "optcg_cards_total" in body


def test_api_cards_list_and_filter(client):
    resp = client.get("/api/cards")
    assert resp.status_code == 200
    all_cards = resp.get_json()
    assert len(all_cards) == 48

    resp = client.get("/api/cards?type=Leader")
    leaders = resp.get_json()
    assert all(c["type"] == "Leader" for c in leaders)
    assert len(leaders) == 3


def test_api_card_detail_and_404(client):
    resp = client.get("/api/cards/OP17-080")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Usopp"

    resp = client.get("/api/cards/NOPE-000")
    assert resp.status_code == 404


def test_api_deck_create_requires_valid_leader(client):
    resp = client.post("/api/decks", json={"name": "Bad", "leader_code": "OP17-080"})
    assert resp.status_code == 400

    resp = client.post("/api/decks", json={"name": "", "leader_code": "OP17-079"})
    assert resp.status_code == 400


def test_api_deck_full_crud_lifecycle(client):
    resp = client.post("/api/decks", json={"name": "API Deck", "leader_code": "OP17-020"})
    assert resp.status_code == 201
    deck = resp.get_json()
    deck_id = deck["id"]

    resp = client.post(f"/api/decks/{deck_id}/cards", json={"card_code": "OP12-034", "quantity": 4})
    assert resp.status_code == 201
    assert resp.get_json()["total_cards"] == 4

    resp = client.get(f"/api/decks/{deck_id}")
    payload = resp.get_json()
    assert payload["legal"] is True
    assert payload["errors"] == []

    resp = client.post(f"/api/decks/{deck_id}/cards", json={"card_code": "OP17-080", "quantity": 1})
    payload = client.get(f"/api/decks/{deck_id}").get_json()
    assert payload["legal"] is False  # OP17-080 is Red, deck leader is Green

    resp = client.delete(f"/api/decks/{deck_id}/cards/OP17-080")
    assert resp.status_code == 204

    resp = client.delete(f"/api/decks/{deck_id}/cards/OP17-080")
    assert resp.status_code == 404

    resp = client.delete(f"/api/decks/{deck_id}")
    assert resp.status_code == 204
    resp = client.get(f"/api/decks/{deck_id}")
    assert resp.status_code == 404


def test_api_deck_add_card_rejects_unknown_card(client):
    resp = client.post("/api/decks", json={"name": "X", "leader_code": "OP17-079"})
    deck_id = resp.get_json()["id"]
    resp = client.post(f"/api/decks/{deck_id}/cards", json={"card_code": "NOPE-000", "quantity": 1})
    assert resp.status_code == 400


def test_api_deck_add_card_rejects_bad_quantity(client):
    resp = client.post("/api/decks", json={"name": "X", "leader_code": "OP17-079"})
    deck_id = resp.get_json()["id"]
    resp = client.post(f"/api/decks/{deck_id}/cards", json={"card_code": "OP17-080", "quantity": 0})
    assert resp.status_code == 400


def test_api_decks_list_and_404_for_unknown(client):
    resp = client.get("/api/decks")
    assert resp.status_code == 200
    resp = client.get("/api/decks/does-not-exist")
    assert resp.status_code == 404
