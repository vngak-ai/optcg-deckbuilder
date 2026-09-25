# OPTCG Deck Builder

A fan-made web app for the One Piece Card Game (OPTCG): browse a card catalogue, view card
detail pages, and build/validate decks against the game's real deck-building rules.

## Features
- Card database with search/filter by name, type, color (48 real cards across 3 leaders)
- Card detail pages with auto-generated, original SVG card art (no official artwork used)
- Deck builder: create decks, add/remove cards, live legality checking
  (50-card limit, max 4 copies per card, unlimited copies for cards that say so,
  card color must match leader color)
- REST JSON API mirroring every UI action (`/api/cards`, `/api/decks`, ...)
- `/health` and `/metrics` (Prometheus) for operational monitoring

## Tech stack
Python 3.12, Flask, Jinja2, prometheus-client, pytest, Docker, Docker Compose, Jenkins,
SonarCloud, pip-audit, Bandit, Trivy.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest --cov=app
python wsgi.py            # http://localhost:3000
```

## CI/CD pipeline (Jenkinsfile)
Build -> Test -> Code Quality -> Security -> Deploy (Staging :3101) -> Release (Production :3100)

## Copyright note
Card names, stats, and rules text are factual game data used for reference. No official
Bandai/Toei/Shueisha artwork is included; all card images in this app are generated
programmatically from plain shapes and text (see `app/cardart.py`).
