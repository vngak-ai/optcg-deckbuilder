"""Simple in-memory user authentication.

Not meant for real production use (no persistence, no rate limiting), but
follows basic security hygiene: passwords are never stored or logged in
plain text, only as a salted hash via werkzeug.security.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from werkzeug.security import check_password_hash, generate_password_hash

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
MIN_PASSWORD_LEN = 8


@dataclass
class User:
    username: str
    password_hash: str
    favorite_codes: List[str] = field(default_factory=list)


class UserStore:
    """In-memory user repository. Case-insensitive usernames."""

    def __init__(self):
        self._users: Dict[str, User] = {}

    def _key(self, username: str) -> str:
        return username.lower()

    def get(self, username: str) -> Optional[User]:
        return self._users.get(self._key(username))

    def exists(self, username: str) -> bool:
        return self._key(username) in self._users

    def register(self, username: str, password: str) -> List[str]:
        """Create a new user. Returns a list of validation errors (empty = success)."""
        errors = []
        if not USERNAME_RE.match(username or ""):
            errors.append("Username must be 3-20 characters: letters, numbers, underscore only")
        elif self.exists(username):
            errors.append("Username is already taken")
        if not password or len(password) < MIN_PASSWORD_LEN:
            errors.append(f"Password must be at least {MIN_PASSWORD_LEN} characters")
        if errors:
            return errors
        user = User(username=username, password_hash=generate_password_hash(password))
        self._users[self._key(username)] = user
        return []

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.get(username)
        if user is None:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user

    def add_favorite(self, username: str, card_code: str) -> bool:
        user = self.get(username)
        if user is None:
            return False
        if card_code not in user.favorite_codes:
            user.favorite_codes.append(card_code)
        return True

    def remove_favorite(self, username: str, card_code: str) -> bool:
        user = self.get(username)
        if user is None:
            return False
        if card_code in user.favorite_codes:
            user.favorite_codes.remove(card_code)
        return True

    def clear(self) -> None:
        self._users.clear()
