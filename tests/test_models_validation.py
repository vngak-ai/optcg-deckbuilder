from app.models import Card, Deck, DeckEntry
from app.store import CardStore
from app.validation import MAX_COPIES, MAX_DECK_SIZE, validate_deck

LEADER_RED = Card(code="L1", name="Leader Red", type="Leader", color=["Red"], traits=[], life=5, power=5000)
CHAR_RED = Card(code="C1", name="Red Guy", type="Character", color=["Red"], traits=[], cost=2, power=2000)
CHAR_BLUE = Card(code="C2", name="Blue Guy", type="Character", color=["Blue"], traits=[], cost=2, power=2000)
UNLIMITED = Card(
    code="C3", name="Prisoner", type="Character", color=["Red"], traits=[], cost=6, power=6000,
    effect="Under the rules of this game, you may have any number of this card in your deck.",
)

CARDS_BY_CODE = {c.code: c for c in [LEADER_RED, CHAR_RED, CHAR_BLUE, UNLIMITED]}


def make_deck(entries):
    return Deck(id="d1", name="Test", leader_code="L1", entries=entries)


def test_legal_deck_has_no_errors():
    deck = make_deck([DeckEntry("C1", 4)])
    assert validate_deck(deck, CARDS_BY_CODE) == []


def test_unknown_leader_reported():
    deck = Deck(id="d1", name="Test", leader_code="NOPE", entries=[])
    errors = validate_deck(deck, CARDS_BY_CODE)
    assert "Unknown leader card: NOPE" in errors


def test_off_color_card_is_rejected():
    deck = make_deck([DeckEntry("C2", 1)])
    errors = validate_deck(deck, CARDS_BY_CODE)
    assert any("does not match leader color" in e for e in errors)


def test_more_than_max_copies_is_rejected():
    deck = make_deck([DeckEntry("C1", MAX_COPIES + 1)])
    errors = validate_deck(deck, CARDS_BY_CODE)
    assert any("max 4 copies" in e for e in errors)


def test_unlimited_card_bypasses_copy_limit():
    deck = make_deck([DeckEntry("C3", 12)])
    assert validate_deck(deck, CARDS_BY_CODE) == []


def test_deck_over_50_cards_is_rejected():
    deck = make_deck([DeckEntry("C1", 4)] * 13)  # 52 cards total
    errors = validate_deck(deck, CARDS_BY_CODE)
    assert any(f"maximum is {MAX_DECK_SIZE}" in e for e in errors)


def test_leader_card_cannot_be_a_deck_entry():
    deck = make_deck([DeckEntry("L1", 1)])
    errors = validate_deck(deck, CARDS_BY_CODE)
    assert any("cannot be a deck card" in e for e in errors)


def test_card_is_unlimited_flag():
    assert UNLIMITED.is_unlimited is True
    assert CHAR_RED.is_unlimited is False


def test_real_seed_data_loads_and_leaders_exist():
    store = CardStore()
    leaders = [c for c in store.all() if c.type == "Leader"]
    assert len(leaders) == 3
    codes = {c.code for c in store.all()}
    assert "OP17-080" in codes  # Usopp
    assert "OP17-020" in codes  # Shanks leader
