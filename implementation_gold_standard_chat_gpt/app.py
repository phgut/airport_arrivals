import os
import logging
from typing import Any, Dict, List
from flask import Flask, request, jsonify, render_template
from marshmallow import Schema, fields, ValidationError
import requests

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configuration
API_KEY = os.getenv("FLIGHTAPI_IO_KEY", "674d8398e8f3d4c048392b6f")
FLIGHTAPI_URL = "https://api.flightapi.io/compschedule/{key}?mode=arrivals&iata={iata}"

class SearchSchema(Schema):
    """Schema for validating search request input."""
    airport_code = fields.Str(required=True, validate=lambda x: len(x) == 3 and x.isalpha())

class ExternalAPIError(Exception):
    """Custom exception for external API-related issues."""
    pass

@app.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError):
    logger.warning("Validation error: %s", e.messages)
    return jsonify({"error": "Invalid input", "details": e.messages}), 400

@app.errorhandler(ExternalAPIError)
def handle_external_api_error(e: ExternalAPIError):
    logger.error("External API error: %s", str(e))
    return jsonify({"error": "Failed to retrieve flight data", "details": str(e)}), 502

@app.errorhandler(Exception)
def handle_general_exception(e: Exception):
    logger.exception("Unhandled exception: %s", str(e))
    return jsonify({"error": "Internal server error"}), 500

def fetch_flights(airport_code: str) -> List[Dict[str, Any]]:
    url = FLIGHTAPI_URL.format(key=API_KEY, iata=airport_code)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ExternalAPIError(f"Network or request issue: {exc}")

    try:
        flights = response.json()
    except ValueError as exc:
        raise ExternalAPIError(f"Invalid JSON response: {exc}")

    if not isinstance(flights, list):
        raise ExternalAPIError("API response structure unexpected: expected a list.")

    arrivals = []
    for page in flights:
        schedule = (
            page.get("airport", {})
                .get("pluginData", {})
                .get("schedule", {})
                .get("arrivals", {})
                .get("data", [])
        )

        if not isinstance(schedule, list):
            continue

        for flight in schedule:
            try:
                airline = flight["flight"]["airline"]["name"]
                flight_number = flight["flight"]["identification"]["number"]["default"]
                origin = flight["flight"]["airport"]["origin"]["name"]
                origin_country = flight["flight"]["airport"]["origin"]["position"]["country"]["name"]
                scheduled_arrival = flight["flight"]["time"]["scheduled"]["arrival"]
                arrivals.append({
                    "airline": airline,
                    "flight_number": flight_number,
                    "origin": origin,
                    "origin_country": origin_country,
                    "scheduled_arrival": scheduled_arrival
                })
            except (KeyError, TypeError):
                logger.warning("Encountered flight with missing/malformed data. Skipping entry.")

    return arrivals

def summarize_by_country(arrivals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summary = {}
    for arrival in arrivals:
        country = arrival.get("origin_country", "Unknown")
        summary[country] = summary.get(country, 0) + 1

    return [{"country": c, "count": cnt} for c, cnt in sorted(summary.items(), key=lambda x: x[1], reverse=True)]

@app.route("/search", methods=["POST"])
def search():
    schema = SearchSchema()
    payload = request.get_json(force=True, silent=True) or {}
    data = schema.load(payload)

    airport_code = data["airport_code"].upper()
    arrivals = fetch_flights(airport_code)
    summary = summarize_by_country(arrivals)

    return jsonify({"arrivals": arrivals, "summary": summary}), 200

@app.route("/", methods=["GET"])
def index():
    # Render the front-end page
    return render_template("index.html")
