"""Deck-building rules for OPTCG (One Piece Card Game).

Real rules this enforces:
  - A deck must have exactly one Leader.
  - A deck has exactly 50 non-Leader cards.
  - At most 4 copies of any given card, UNLESS the card's own text grants
    unlimited copies (e.g. "Prisoner of Impel Down").
  - Every non-Leader card must share at least one color with the Leader.
"""
from __future__ import annotations

from typing import Dict, List

from .models import Card, Deck

MAX_DECK_SIZE = 50
MAX_COPIES = 4


def validate_deck(deck: Deck, cards_by_code: Dict[str, Card]) -> List[str]:
    errors: List[str] = []

    leader = cards_by_code.get(deck.leader_code)
    if leader is None:
        return [f"Unknown leader card: {deck.leader_code}"]
    if leader.type != "Leader":
        errors.append(f"{deck.leader_code} is not a Leader card")

    total = deck.total_non_leader_cards()
    if total > MAX_DECK_SIZE:
        errors.append(f"Deck has {total} cards, maximum is {MAX_DECK_SIZE}")

    for entry in deck.entries:
        card = cards_by_code.get(entry.card_code)
        if card is None:
            errors.append(f"Unknown card: {entry.card_code}")
            continue
        if card.type == "Leader":
            errors.append(f"{card.name} ({card.code}) is a Leader and cannot be a deck card")
            continue
        if not card.is_unlimited and entry.quantity > MAX_COPIES:
            errors.append(f"{card.name} ({card.code}): max {MAX_COPIES} copies allowed, has {entry.quantity}")
        if leader is not None and card.color and leader.color:
            if not set(card.color) & set(leader.color):
                errors.append(
                    f"{card.name} ({card.code}) color {card.color} does not match leader color {leader.color}"
                )

    return errors


def is_deck_legal(deck: Deck, cards_by_code: Dict[str, Card]) -> bool:
    return len(validate_deck(deck, cards_by_code)) == 0
