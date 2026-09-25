from app.cardart import render_card_svg
from app.store import CardStore


def test_render_card_svg_contains_name_and_code():
    store = CardStore()
    card = store.get("OP17-080")
    svg = render_card_svg(card)
    assert svg.startswith("<svg")
    assert "Usopp" in svg
    assert "OP17-080" in svg
    assert str(card.power) in svg


def test_render_card_svg_escapes_html():
    from app.models import Card
    card = Card(code="X1", name="<script>alert(1)</script>", type="Character", color=["Red"], traits=[])
    svg = render_card_svg(card)
    assert "<script>alert" not in svg
    assert "&lt;script&gt;" in svg


def test_render_card_svg_handles_leader_with_life_not_cost():
    store = CardStore()
    leader = store.get("OP17-079")
    svg = render_card_svg(leader)
    assert f"L{leader.life}" in svg
