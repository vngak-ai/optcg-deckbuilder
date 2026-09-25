"""Generate a simple, original SVG 'card art' placeholder for a card.

This deliberately does NOT reproduce any official Bandai artwork. It only
uses factual game data (name, cost, power, type, color) to draw a generic
card-shaped graphic, in the spirit of a custom fan-made card back.
"""
from __future__ import annotations

import html

from .models import Card

COLOR_HEX = {
    "Red": "#c0392b",
    "Green": "#1e8449",
    "Blue": "#2471a3",
    "Purple": "#7d3c98",
    "Black": "#2c2c2c",
    "Yellow": "#d4ac0d",
}

ATTRIBUTE_ICON = {
    "Slash": "\u2694",       # crossed swords
    "Strike": "\u270a",      # fist
    "Ranged": "\u27b3",      # arrow
    "Special": "\u2726",     # star
    "Wisdom": "\U0001F9E0",  # brain
}


def _gradient_colors(colors: list[str]) -> tuple[str, str]:
    hexes = [COLOR_HEX.get(c, "#555555") for c in colors] or ["#555555"]
    if len(hexes) == 1:
        return hexes[0], hexes[0]
    return hexes[0], hexes[1]


def render_card_svg(card: Card) -> str:
    c1, c2 = _gradient_colors(card.color)
    name = html.escape(card.name)
    type_label = html.escape(card.type.upper())
    trait_line = html.escape(" / ".join(card.traits)) if card.traits else ""
    grad_id = f"grad-{card.code}"

    top_left = ""
    if card.cost is not None:
        top_left = f'<circle cx="46" cy="46" r="34" fill="white" opacity="0.92"/>' \
                    f'<text x="46" y="58" font-size="34" font-weight="700" text-anchor="middle" fill="{c1}">{card.cost}</text>'
    elif card.life is not None:
        top_left = f'<circle cx="46" cy="46" r="34" fill="white" opacity="0.92"/>' \
                    f'<text x="46" y="58" font-size="30" font-weight="700" text-anchor="middle" fill="{c1}">L{card.life}</text>'

    power_block = ""
    if card.power is not None:
        icon = ATTRIBUTE_ICON.get(card.attribute or "", "")
        power_block = (
            f'<text x="330" y="52" font-size="34" font-weight="700" text-anchor="end" fill="white">{card.power}</text>'
            f'<text x="330" y="76" font-size="16" text-anchor="end" fill="white" opacity="0.85">{html.escape(icon)} {html.escape(card.attribute or "")}</text>'
        )

    counter_block = ""
    if card.counter:
        counter_block = (
            f'<rect x="8" y="190" width="46" height="120" rx="10" fill="white" opacity="0.15"/>'
            f'<text x="31" y="200" font-size="12" text-anchor="middle" fill="white" '
            f'transform="rotate(-90 31 250)">COUNTER +{card.counter}</text>'
        )

    svg = f'''<svg viewBox="0 0 360 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{name}">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="352" height="492" rx="22" fill="url(#{grad_id})" stroke="white" stroke-width="4"/>
  <rect x="18" y="330" width="324" height="150" rx="12" fill="white" opacity="0.92"/>
  {top_left}
  {power_block}
  {counter_block}
  <text x="180" y="365" font-size="26" font-weight="700" text-anchor="middle" fill="#1a1a1a">{name}</text>
  <text x="180" y="388" font-size="13" text-anchor="middle" fill="#555555">{trait_line}</text>
  <rect x="18" y="400" width="324" height="66" rx="8" fill="#f4f4f4"/>
  <text x="180" y="420" font-size="11" text-anchor="middle" fill="#333333">
    <tspan x="180" dy="0">{html.escape(card.code)}</tspan>
  </text>
  <rect x="18" y="18" width="120" height="28" rx="14" fill="black" opacity="0.35"/>
  <text x="30" y="38" font-size="14" font-weight="700" fill="white">{type_label}</text>
</svg>'''
    return svg
