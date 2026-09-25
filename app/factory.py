"""Flask application factory."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, url_for

from .auth import UserStore
from .customart import find_custom_art_filename
from .metrics import init_metrics, metrics_bp
from .routes import bp
from .store import CardStore, DeckStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_ART_DIR = PROJECT_ROOT / "static" / "img" / "custom_cards"


def create_app(seed_decks: bool = True) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
    )
    app.config["APP_ENV"] = os.environ.get("APP_ENV", "development")
    app.config["APP_VERSION"] = os.environ.get("APP_VERSION", "dev")
    # SECRET_KEY signs the session cookie. In production this MUST come from
    # an environment variable / secret store, never hardcoded.
    app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

    card_store = CardStore()
    deck_store = DeckStore()
    user_store = UserStore()
    app.config["CARD_STORE"] = card_store
    app.config["DECK_STORE"] = deck_store
    app.config["USER_STORE"] = user_store

    if seed_decks:
        for d in card_store.seed_decks():
            deck_store.create_from_seed(d["name"], d["leader_card"], d.get("cards", []))

    def card_image_url(card):
        """Custom user-supplied art if one exists for this card, else the
        auto-generated SVG placeholder."""
        filename = find_custom_art_filename(card.code, CUSTOM_ART_DIR)
        if filename:
            return url_for("static", filename=f"img/custom_cards/{filename}")
        return url_for("main.card_art", code=card.code)

    app.jinja_env.globals["card_image_url"] = card_image_url

    app.register_blueprint(bp)
    app.register_blueprint(metrics_bp)
    init_metrics(app)
    return app
