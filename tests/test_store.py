from app.store import CardStore, DeckStore


def test_card_store_search_by_name():
    store = CardStore()
    results = store.search(query="shanks")
    assert any(c.code == "OP17-020" for c in results)


def test_card_store_search_by_type_and_color():
    store = CardStore()
    results = store.search(type_="Leader", color="Red")
    assert all(c.type == "Leader" and "Red" in c.color for c in results)


def test_card_store_get_missing_returns_none():
    store = CardStore()
    assert store.get("NOPE-000") is None


def test_deck_store_crud_lifecycle():
    store = DeckStore()
    deck = store.create("My Deck", "OP17-079")
    assert store.get(deck.id) is deck

    store.add_card(deck.id, "OP17-080", 2)
    store.add_card(deck.id, "OP17-080", 1)  # merges into same entry
    updated = store.get(deck.id)
    assert updated.entries[0].card_code == "OP17-080"
    assert updated.entries[0].quantity == 3

    assert store.remove_card(deck.id, "OP17-080") is True
    assert store.get(deck.id).entries == []
    assert store.remove_card(deck.id, "OP17-080") is False

    assert store.delete(deck.id) is True
    assert store.get(deck.id) is None
    assert store.delete(deck.id) is False


def test_deck_store_create_from_seed():
    store = DeckStore()
    deck = store.create_from_seed("Seeded", "OP17-079", ["OP17-080", "OP17-081"])
    assert deck.total_non_leader_cards() == 2
