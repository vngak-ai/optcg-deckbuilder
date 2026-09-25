"""In-memory data stores for cards (read-only, seeded from JSON) and decks (CRUD)."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from .models import Card, Deck, DeckEntry

SEED_PATH = Path(__file__).parent / "data" / "cards_seed.json"


class CardStore:
    """Read-only catalogue of OPTCG cards, loaded once from the seed file."""

    def __init__(self, seed_path: Path = SEED_PATH):
        with open(seed_path, encoding="utf-8") as f:
            raw = json.load(f)
        self._cards: Dict[str, Card] = {}
        for c in raw["cards"]:
            card = Card.from_dict(c)
            self._cards[card.code] = card
        self._seed_decks = raw.get("decks", [])

    def all(self) -> List[Card]:
        return list(self._cards.values())

    def get(self, code: str) -> Optional[Card]:
        return self._cards.get(code)

    def by_codes(self) -> Dict[str, Card]:
        return self._cards

    def search(self, query: str = "", type_: str = "", color: str = "") -> List[Card]:
        results = self.all()
        if query:
            q = query.lower()
            results = [c for c in results if q in c.name.lower() or q in c.code.lower()]
        if type_:
            results = [c for c in results if c.type == type_]
        if color:
            results = [c for c in results if color in c.color]
        return sorted(results, key=lambda c: (c.type, c.name))

    def seed_decks(self) -> list:
        return self._seed_decks


class DeckStore:
    """In-memory CRUD store for user-built decks."""

    def __init__(self):
        self._decks: Dict[str, Deck] = {}

    def list(self) -> List[Deck]:
        return list(self._decks.values())

    def get(self, deck_id: str) -> Optional[Deck]:
        return self._decks.get(deck_id)

    def create(self, name: str, leader_code: str) -> Deck:
        deck = Deck(id=str(uuid.uuid4()), name=name, leader_code=leader_code, entries=[])
        self._decks[deck.id] = deck
        return deck

    def create_from_seed(self, name: str, leader_code: str, card_codes: List[str]) -> Deck:
        deck = self.create(name, leader_code)
        for code in card_codes:
            self.add_card(deck.id, code, 1)
        return deck

    def add_card(self, deck_id: str, card_code: str, quantity: int = 1) -> Optional[Deck]:
        deck = self._decks.get(deck_id)
        if deck is None:
            return None
        for entry in deck.entries:
            if entry.card_code == card_code:
                entry.quantity += quantity
                return deck
        deck.entries.append(DeckEntry(card_code=card_code, quantity=quantity))
        return deck

    def remove_card(self, deck_id: str, card_code: str) -> bool:
        deck = self._decks.get(deck_id)
        if deck is None:
            return False
        before = len(deck.entries)
        deck.entries = [e for e in deck.entries if e.card_code != card_code]
        return len(deck.entries) != before

    def delete(self, deck_id: str) -> bool:
        return self._decks.pop(deck_id, None) is not None

    def clear(self) -> None:
        self._decks.clear()
