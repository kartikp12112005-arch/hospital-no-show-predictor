"""Integration tests for Flask routes: public pages, auth, and CRUD flows."""

import os

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "trained_models", "best_model.pkl")
requires_model = pytest.mark.skipif(
    not os.path.exists(MODEL_PATH), reason="Trained model not found — run `python model/train.py` first."
)


# ---------------------------------------------------------------- Public pages
@pytest.mark.parametrize("route", ["/", "/about", "/predict", "/login"])
def test_public_routes_return_200(client, route):
    assert client.get(route).status_code == 200


def test_unknown_route_returns_404(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404


# --------------------------------------------------------------- Authentication
def test_login_with_valid_credentials_redirects_to_dashboard(client):
    resp = client.post(
        "/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data


def test_login_with_invalid_credentials_stays_on_login(client):
    resp = client.post(
        "/login", data={"username": "admin", "password": "wrong-password"}, follow_redirects=True
    )
    assert b"Invalid username or password" in resp.data


@pytest.mark.parametrize("route", ["/dashboard", "/analytics", "/history", "/model-comparison"])
def test_admin_routes_require_login(client, route):
    resp = client.get(route, follow_redirects=True)
    assert b"Please log in" in resp.data


@pytest.mark.parametrize("route", ["/dashboard", "/analytics", "/history", "/model-comparison"])
def test_admin_routes_accessible_when_logged_in(admin_client, route):
    resp = admin_client.get(route)
    assert resp.status_code == 200


def test_logout_clears_session(admin_client):
    admin_client.get("/logout")
    resp = admin_client.get("/dashboard", follow_redirects=True)
    assert b"Please log in" in resp.data


# ------------------------------------------------------------------ Prediction
@requires_model
def test_predict_get_shows_form(client):
    resp = client.get("/predict")
    assert b"Predict Appointment Attendance" in resp.data


@requires_model
def test_predict_post_valid_data_shows_result(client, valid_predict_payload):
    resp = client.post("/predict", data=valid_predict_payload, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Prediction Result" in resp.data


def test_predict_post_invalid_gender_redirects_with_flash(client):
    payload = {"gender": "Z", "age": "30", "waiting_days": "5"}
    resp = client.post("/predict", data=payload, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Gender must be" in resp.data


@requires_model
def test_api_predict_returns_json(client, valid_predict_payload):
    resp = client.post("/api/predict", json=valid_predict_payload)
    assert resp.status_code == 200
    body = resp.get_json()
    assert "prediction" in body
    assert "confidence" in body


def test_api_predict_missing_field_returns_400(client):
    resp = client.post("/api/predict", json={"gender": "F"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


# ---------------------------------------------------------------------- History
@requires_model
def test_history_shows_saved_prediction(admin_client, valid_predict_payload):
    admin_client.post("/predict", data=valid_predict_payload)
    resp = admin_client.get("/history")
    assert resp.status_code == 200
    assert b"Prediction History" in resp.data


@requires_model
def test_delete_history_record(admin_client, valid_predict_payload):
    admin_client.post("/predict", data=valid_predict_payload)

    # Find the record's ID from the export CSV (simplest reliable source)
    export_resp = admin_client.get("/history/export")
    csv_text = export_resp.data.decode()
    first_data_row = csv_text.strip().split("\n")[1]
    record_id = first_data_row.split(",")[0]

    del_resp = admin_client.post(f"/history/delete/{record_id}", follow_redirects=True)
    assert del_resp.status_code == 200
    assert b"Record deleted" in del_resp.data


def test_export_history_returns_csv(admin_client):
    resp = admin_client.get("/history/export")
    assert resp.status_code == 200
    assert resp.content_type.startswith("text/csv")


# ------------------------------------------------------------------ Dashboard API
def test_dashboard_trend_api_requires_login(client):
    resp = client.get("/api/dashboard-trend", follow_redirects=True)
    assert b"Please log in" in resp.data


def test_dashboard_trend_api_returns_json_shape(admin_client):
    resp = admin_client.get("/api/dashboard-trend")
    assert resp.status_code == 200
    body = resp.get_json()
    assert set(body.keys()) == {"labels", "attend", "no_show"}
