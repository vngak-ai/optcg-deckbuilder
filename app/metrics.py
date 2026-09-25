"""Prometheus metrics for the OPTCG Deck Builder API."""
from __future__ import annotations

import time

from flask import Blueprint, Response, current_app, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

metrics_bp = Blueprint("metrics", __name__)

REQUEST_COUNT = Counter(
    "optcg_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "optcg_http_request_duration_seconds", "HTTP request duration in seconds", ["endpoint"]
)
DECKS_GAUGE = Gauge("optcg_decks_total", "Number of decks currently stored")
CARDS_GAUGE = Gauge("optcg_cards_total", "Number of cards in the catalogue")


@metrics_bp.route("/metrics")
def metrics():
    DECKS_GAUGE.set(len(current_app.config["DECK_STORE"].list()))
    CARDS_GAUGE.set(len(current_app.config["CARD_STORE"].all()))
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def init_metrics(app):
    @app.before_request
    def _start_timer():
        request._start_time = time.time()

    @app.after_request
    def _record(response):
        endpoint = request.endpoint or "unmatched"
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        if hasattr(request, "_start_time"):
            REQUEST_LATENCY.labels(endpoint).observe(time.time() - request._start_time)
        return response
