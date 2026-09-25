"""HTTP routes: JSON API + server-rendered HTML pages."""
from __future__ import annotations

from functools import wraps

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .cardart import render_card_svg
from .models import Deck
from .validation import MAX_COPIES, MAX_DECK_SIZE, validate_deck

bp = Blueprint("main", __name__)


def _card_store():
    return current_app.config["CARD_STORE"]


def _deck_store():
    return current_app.config["DECK_STORE"]


def _user_store():
    return current_app.config["USER_STORE"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("main.login_page", next=request.path))
        return view(*args, **kwargs)

    return wrapped


# ---------- Auth pages ----------

@bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        errors = _user_store().register(username, password)
        if not errors:
            session["username"] = username
            return redirect(url_for("main.collection_page"))
        return render_template("register.html", errors=errors, username=username)
    return render_template("register.html", errors=[], username="")


@bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = _user_store().authenticate(username, password)
        if user is not None:
            session["username"] = user.username
            next_url = request.args.get("next") or url_for("main.collection_page")
            return redirect(next_url)
        return render_template("login.html", error="Invalid username or password", username=username)
    return render_template("login.html", error=None, username="")


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("main.index"))


@bp.route("/collection")
@login_required
def collection_page():
    user = _user_store().get(session["username"])
    cards_by_code = _card_store().by_codes()
    favorites = [cards_by_code[code] for code in user.favorite_codes if code in cards_by_code]
    return render_template("collection.html", favorites=favorites)


@bp.route("/cards/<code>/favorite", methods=["POST"])
@login_required
def toggle_favorite(code):
    if _card_store().get(code) is None:
        return render_template("404.html", what=f"Card {code}"), 404
    user = _user_store().get(session["username"])
    if code in user.favorite_codes:
        _user_store().remove_favorite(session["username"], code)
    else:
        _user_store().add_favorite(session["username"], code)
    return redirect(url_for("main.card_detail", code=code))


# ---------- HTML pages ----------

@bp.route("/")
def index():
    q = request.args.get("q", "")
    type_ = request.args.get("type", "")
    color = request.args.get("color", "")
    cards = _card_store().search(q, type_, color)
    return render_template("cards.html", cards=cards, q=q, type_=type_, color=color)


@bp.route("/cards/<code>")
def card_detail(code):
    card = _card_store().get(code)
    if card is None:
        return render_template("404.html", what=f"Card {code}"), 404
    is_favorite = False
    if "username" in session:
        user = _user_store().get(session["username"])
        is_favorite = user is not None and code in user.favorite_codes
    return render_template("card_detail.html", card=card, is_favorite=is_favorite)


@bp.route("/cards/<code>/art.svg")
def card_art(code):
    card = _card_store().get(code)
    if card is None:
        return "", 404
    svg = render_card_svg(card)
    return svg, 200, {"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}


@bp.route("/decks")
def decks_page():
    decks = _deck_store().list()
    cards_by_code = _card_store().by_codes()
    summaries = []
    for d in decks:
        leader = cards_by_code.get(d.leader_code)
        summaries.append({"deck": d, "leader": leader, "errors": validate_deck(d, cards_by_code)})
    return render_template("decks.html", summaries=summaries)


@bp.route("/decks/new", methods=["GET", "POST"])
def deck_new():
    leaders = [c for c in _card_store().all() if c.type == "Leader"]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        leader_code = request.form.get("leader_code", "")
        if name and _card_store().get(leader_code):
            deck = _deck_store().create(name, leader_code)
            return render_template("deck_detail.html", **_deck_detail_context(deck.id))
    return render_template("deck_new.html", leaders=leaders)


def _deck_detail_context(deck_id):
    deck = _deck_store().get(deck_id)
    cards_by_code = _card_store().by_codes()
    leader = cards_by_code.get(deck.leader_code) if deck else None
    rows = []
    if deck:
        for entry in deck.entries:
            rows.append({"card": cards_by_code.get(entry.card_code), "quantity": entry.quantity})
    errors = validate_deck(deck, cards_by_code) if deck else ["Deck not found"]
    return {
        "deck": deck,
        "leader": leader,
        "rows": rows,
        "errors": errors,
        "max_deck_size": MAX_DECK_SIZE,
        "max_copies": MAX_COPIES,
        "all_cards": [c for c in _card_store().all() if c.type != "Leader"],
    }


@bp.route("/decks/<deck_id>")
def deck_detail(deck_id):
    deck = _deck_store().get(deck_id)
    if deck is None:
        return render_template("404.html", what=f"Deck {deck_id}"), 404
    return render_template("deck_detail.html", **_deck_detail_context(deck_id))


@bp.route("/decks/<deck_id>/cards", methods=["POST"])
def deck_add_card_form(deck_id):
    card_code = request.form.get("card_code", "")
    quantity = int(request.form.get("quantity", 1) or 1)
    if _card_store().get(card_code):
        _deck_store().add_card(deck_id, card_code, quantity)
    deck = _deck_store().get(deck_id)
    if deck is None:
        return render_template("404.html", what=f"Deck {deck_id}"), 404
    return render_template("deck_detail.html", **_deck_detail_context(deck_id))


@bp.route("/decks/<deck_id>/cards/<card_code>/remove", methods=["POST"])
def deck_remove_card_form(deck_id, card_code):
    _deck_store().remove_card(deck_id, card_code)
    return render_template("deck_detail.html", **_deck_detail_context(deck_id))


@bp.route("/decks/<deck_id>/delete", methods=["POST"])
def deck_delete_form(deck_id):
    _deck_store().delete(deck_id)
    from flask import redirect, url_for
    return redirect(url_for("main.decks_page"))


# ---------- JSON API ----------

@bp.route("/health")
def health():
    return jsonify(status="ok", environment=current_app.config.get("APP_ENV", "development"),
                    version=current_app.config.get("APP_VERSION", "dev"))


@bp.route("/api/cards")
def api_cards():
    q = request.args.get("q", "")
    type_ = request.args.get("type", "")
    color = request.args.get("color", "")
    cards = _card_store().search(q, type_, color)
    return jsonify([c.to_dict() for c in cards])


@bp.route("/api/cards/<code>")
def api_card_detail(code):
    card = _card_store().get(code)
    if card is None:
        return jsonify(error="Card not found"), 404
    return jsonify(card.to_dict())


@bp.route("/api/decks", methods=["GET", "POST"])
def api_decks():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        leader_code = data.get("leader_code", "")
        if not name:
            return jsonify(errors=["name is required"]), 400
        leader = _card_store().get(leader_code)
        if leader is None or leader.type != "Leader":
            return jsonify(errors=["leader_code must reference a Leader card"]), 400
        deck = _deck_store().create(name, leader_code)
        return jsonify(deck.to_dict()), 201
    return jsonify([d.to_dict() for d in _deck_store().list()])


@bp.route("/api/decks/<deck_id>")
def api_deck_detail(deck_id):
    deck = _deck_store().get(deck_id)
    if deck is None:
        return jsonify(error="Deck not found"), 404
    errors = validate_deck(deck, _card_store().by_codes())
    payload = deck.to_dict()
    payload["errors"] = errors
    payload["legal"] = len(errors) == 0
    return jsonify(payload)


@bp.route("/api/decks/<deck_id>/cards", methods=["POST"])
def api_deck_add_card(deck_id):
    if _deck_store().get(deck_id) is None:
        return jsonify(error="Deck not found"), 404
    data = request.get_json(silent=True) or {}
    card_code = data.get("card_code", "")
    raw_quantity = data.get("quantity", 1)
    quantity = int(raw_quantity) if raw_quantity is not None else 1
    if quantity < 1:
        return jsonify(errors=["quantity must be at least 1"]), 400
    card = _card_store().get(card_code)
    if card is None:
        return jsonify(errors=[f"Unknown card: {card_code}"]), 400
    _deck_store().add_card(deck_id, card_code, quantity)
    deck = _deck_store().get(deck_id)
    return jsonify(deck.to_dict()), 201


@bp.route("/api/decks/<deck_id>/cards/<card_code>", methods=["DELETE"])
def api_deck_remove_card(deck_id, card_code):
    if _deck_store().get(deck_id) is None:
        return jsonify(error="Deck not found"), 404
    removed = _deck_store().remove_card(deck_id, card_code)
    if not removed:
        return jsonify(error="Card not in deck"), 404
    return "", 204


@bp.route("/api/decks/<deck_id>", methods=["DELETE"])
def api_deck_delete(deck_id):
    if not _deck_store().delete(deck_id):
        return jsonify(error="Deck not found"), 404
    return "", 204
