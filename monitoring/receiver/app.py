"""Minimal alert-notification receiver.

Stands in for a real notification channel (Slack, email, PagerDuty, ...).
It receives Alertmanager's webhook payload and logs each alert to stdout,
so the Jenkins Monitoring stage can prove an alert was actually delivered
to "the team" by checking this container's logs.
"""
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/alerts", methods=["POST"])
def receive_alert():
    payload = request.get_json(silent=True) or {}
    for alert in payload.get("alerts", []):
        name = alert.get("labels", {}).get("alertname", "unknown")
        status = alert.get("status", "unknown")
        summary = alert.get("annotations", {}).get("summary", "")
        print(f"ALERT [{status}] {name}: {summary}", flush=True)
    return jsonify(received=True), 200


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
