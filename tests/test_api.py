import csv
import io
from fastapi.testclient import TestClient
from server import app, selection
from analysis.metrics import summarize

client = TestClient(app)


def test_dashboard_matches_independent_metric_model():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    result = response.json()
    assert result["summary"] == summarize(selection())
    assert len(result["cohorts"]["labels"]) == 12
    assert len(result["orders"]) == 2400


def test_filters_and_csv_export_use_the_same_rows():
    query = {"country":"Germany", "category":"Home"}
    result = client.get("/api/dashboard",params=query).json()
    expected = selection(country="Germany",category="Home")
    assert result["summary"] == summarize(expected)
    response = client.get("/api/export",params=query)
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == len(expected)
    assert {row["country"] for row in rows} == {"Germany"}
    assert {row["category"] for row in rows} == {"Home"}


def test_empty_dates_are_valid_but_bad_dates_are_rejected():
    result = client.get("/api/dashboard",params={"start":"2027-01-01"}).json()
    assert result["summary"]["revenue"] == 0
    assert result["cohorts"]["labels"] == []
    assert client.get("/api/dashboard",params={"start":"not-a-date"}).status_code == 422


def test_react_distribution_and_health_are_served():
    assert client.get("/health").json()["status"] == "ok"
    html = client.get("/")
    assert html.status_code == 200
    assert 'id="root"' in html.text
    assert "/assets/" in html.text
