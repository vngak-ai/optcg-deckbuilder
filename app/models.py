"""Data classes for OPTCG cards and decks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Card:
    code: str
    name: str
    type: str  # Leader | Character | Event
    color: List[str]
    traits: List[str]
    effect: str = ""
    cost: Optional[int] = None
    power: Optional[int] = None
    counter: Optional[int] = None
    life: Optional[int] = None
    attribute: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> "Card":
        return Card(
            code=d["code"],
            name=d["name"],
            type=d["type"],
            color=list(d.get("color", [])),
            traits=list(d.get("traits", [])),
            effect=d.get("effect") or "",
            cost=d.get("cost"),
            power=d.get("power"),
            counter=d.get("counter"),
            life=d.get("life"),
            attribute=d.get("attribute"),
        )

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "type": self.type,
            "color": self.color,
            "traits": self.traits,
            "effect": self.effect,
            "cost": self.cost,
            "power": self.power,
            "counter": self.counter,
            "life": self.life,
            "attribute": self.attribute,
        }

    @property
    def is_unlimited(self) -> bool:
        """Cards like 'Prisoner of Impel Down' explicitly allow any number of copies."""
        return "any number of this card in your deck" in self.effect.lower()


@dataclass
class DeckEntry:
    card_code: str
    quantity: int = 1


@dataclass
class Deck:
    id: str
    name: str
    leader_code: str
    entries: List[DeckEntry] = field(default_factory=list)

    def total_non_leader_cards(self) -> int:
        return sum(e.quantity for e in self.entries)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "leader_code": self.leader_code,
            "entries": [{"card_code": e.card_code, "quantity": e.quantity} for e in self.entries],
            "total_cards": self.total_non_leader_cards(),
        }
