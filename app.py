
import csv
import io
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import (
    Flask,        
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from utils.auth import login_required, verify_admin
from utils.db import get_db_connection, init_db
from utils.logger import log_event
from utils.validators import ValidationError, validate_predict_form

load_dotenv()

try:
    from utils.predictor import predict_no_show

    MODEL_AVAILABLE = True
except Exception:
    MODEL_AVAILABLE = False


def create_app(database_path: str = None) -> Flask:
    """
    Application factory: builds and configures the Flask app instance.

    Args:
        database_path: Optional override for the SQLite file path.
            Used by the test suite to point at an isolated temp database
            instead of the real database/hospital.db.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["DATABASE"] = database_path or os.path.join(
        os.path.dirname(__file__), "database", "hospital.db"
    )

    with app.app_context():
        init_db(app.config["DATABASE"])

    register_routes(app)
    register_error_handlers(app)
    return app


def register_routes(app: Flask) -> None:
    """Attach all URL routes to the Flask app instance."""

    # ---------------------------------------------------------------- Home
    @app.route("/")
    def home():
        return render_template("index.html")

    # --------------------------------------------------------------- About
    @app.route("/about")
    def about():
        metadata = None
        if MODEL_AVAILABLE:
            from utils.predictor import get_model_metadata

            metadata = get_model_metadata()
        return render_template("about.html", metadata=metadata)

    # ------------------------------------------------------------- Predict
    @app.route("/predict", methods=["GET", "POST"])
    def predict():
        if request.method == "GET":
            return render_template("predict.html")

        try:
            form_data = validate_predict_form(request.form)
        except ValidationError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("predict"))

        if not MODEL_AVAILABLE:
            flash(
                "The prediction model hasn't been trained yet. "
                "Run the training pipeline (Step 3) to enable predictions.",
                "warning",
            )
            return redirect(url_for("predict"))

        try:
            result = predict_no_show(form_data)
        except Exception as exc:
            log_event(app.config["DATABASE"], "ERROR", f"Prediction failed: {exc}")
            flash("Something went wrong while generating the prediction.", "danger")
            return redirect(url_for("predict"))

        _save_prediction(app, form_data, result)
        session["last_prediction"] = {"form_data": form_data, "result": result}
        return render_template("result.html", result=result, form_data=form_data)

    # --------------------------------------------------------- JSON API
    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        if not MODEL_AVAILABLE:
            return jsonify({"error": "Prediction model is not available yet."}), 503

        try:
            payload = request.get_json(force=True, silent=True) or {}
            form_data = validate_predict_form(payload)
            result = predict_no_show(form_data)
            _save_prediction(app, form_data, result)
            return jsonify(result), 200
        except ValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            log_event(app.config["DATABASE"], "ERROR", f"API prediction failed: {exc}")
            return jsonify({"error": "Internal server error."}), 500

    # ----------------------------------------------------------------- Auth
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection(app.config["DATABASE"])
        admin_row = conn.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()
        conn.close()

        if admin_row and verify_admin(password, admin_row["password_hash"]):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    # ------------------------------------------------------------ Dashboard
    @app.route("/dashboard")
    @login_required
    def dashboard():
        conn = get_db_connection(app.config["DATABASE"])
        total = conn.execute("SELECT COUNT(*) AS c FROM prediction_history").fetchone()["c"]
        attend = conn.execute(
            "SELECT COUNT(*) AS c FROM prediction_history WHERE prediction = 'Attend'"
        ).fetchone()["c"]
        no_show = conn.execute(
            "SELECT COUNT(*) AS c FROM prediction_history WHERE prediction = 'No-Show'"
        ).fetchone()["c"]
        recent = conn.execute(
            "SELECT * FROM prediction_history ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
        conn.close()

        return render_template(
            "dashboard.html", total=total, attend=attend, no_show=no_show, recent=recent
        )

    # ------------------------------------------------------ Model Comparison
    @app.route("/model-comparison")
    @login_required
    def model_comparison():
        if not MODEL_AVAILABLE:
            flash("Model metrics are unavailable until the training pipeline has been run.", "warning")
            return render_template("model_comparison.html", metadata=None)

        from utils.predictor import get_model_metadata

        metadata = get_model_metadata()
        return render_template("model_comparison.html", metadata=metadata)

    # -------------------------------------------------- Dashboard trend API
    @app.route("/api/dashboard-trend")
    @login_required
    def dashboard_trend():
        """Daily prediction counts for the last 14 days, used by Chart.js."""
        conn = get_db_connection(app.config["DATABASE"])
        rows = conn.execute(
            """
            SELECT substr(created_at, 1, 10) AS day,
                   SUM(CASE WHEN prediction = 'Attend' THEN 1 ELSE 0 END) AS attend,
                   SUM(CASE WHEN prediction = 'No-Show' THEN 1 ELSE 0 END) AS no_show
            FROM prediction_history
            GROUP BY day
            ORDER BY day DESC
            LIMIT 14
            """
        ).fetchall()
        conn.close()

        rows = list(reversed(rows))
        return jsonify(
            {
                "labels": [r["day"] for r in rows],
                "attend": [r["attend"] for r in rows],
                "no_show": [r["no_show"] for r in rows],
            }
        )

    # ------------------------------------------------------ PDF report
    @app.route("/report/download")
    def download_report():
        last = session.get("last_prediction")
        if not last:
            flash("No recent prediction found. Please make a prediction first.", "warning")
            return redirect(url_for("predict"))

        from utils.report import generate_prediction_report

        pdf_buffer = generate_prediction_report(last["form_data"], last["result"])
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="prediction_report.pdf",
        )

    # ------------------------------------------------------------ Analytics
    @app.route("/analytics")
    @login_required
    def analytics():
        stats_path = os.path.join(os.path.dirname(__file__), "trained_models", "dataset_stats.json")
        stats = None
        if os.path.exists(stats_path):
            import json

            with open(stats_path, "r", encoding="utf-8") as f:
                stats = json.load(f)
        return render_template("analytics.html", stats=stats)

    # -------------------------------------------------------------- History
    @app.route("/history")
    @login_required
    def history():
        conn = get_db_connection(app.config["DATABASE"])
        search_term = request.args.get("search", "").strip()

        if search_term:
            records = conn.execute(
                "SELECT * FROM prediction_history WHERE CAST(id AS TEXT) LIKE ? "
                "ORDER BY created_at DESC",
                (f"%{search_term}%",),
            ).fetchall()
        else:
            records = conn.execute(
                "SELECT * FROM prediction_history ORDER BY created_at DESC"
            ).fetchall()

        conn.close()
        return render_template("history.html", records=records)

    @app.route("/history/delete/<int:record_id>", methods=["POST"])
    @login_required
    def delete_history(record_id):
        conn = get_db_connection(app.config["DATABASE"])
        conn.execute("DELETE FROM prediction_history WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        flash("Record deleted.", "success")
        return redirect(url_for("history"))

    @app.route("/history/export")
    @login_required
    def export_history():
        conn = get_db_connection(app.config["DATABASE"])
        records = conn.execute("SELECT * FROM prediction_history ORDER BY created_at DESC").fetchall()
        conn.close()

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["ID", "Age", "Gender", "Prediction", "Confidence", "Risk Level", "Waiting Days", "Created At"]
        )
        for row in records:
            writer.writerow(
                [
                    row["id"],
                    row["patient_age"],
                    row["gender"],
                    row["prediction"],
                    row["confidence"],
                    row["risk_level"],
                    row["waiting_days"],
                    row["created_at"],
                ]
            )

        buffer.seek(0)
        return send_file(
            io.BytesIO(buffer.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="prediction_history.csv",
        )


def _save_prediction(app: Flask, form_data: dict, result: dict) -> None:
    """Persist a single prediction result to the prediction_history table."""
    conn = get_db_connection(app.config["DATABASE"])
    conn.execute(
        """
        INSERT INTO prediction_history
            (patient_age, gender, scholarship, hypertension, diabetes, alcoholism,
             handicap, sms_received, waiting_days, prediction, confidence,
             risk_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            form_data["age"],
            form_data["gender"],
            form_data["scholarship"],
            form_data["hypertension"],
            form_data["diabetes"],
            form_data["alcoholism"],
            form_data["handicap"],
            form_data["sms_received"],
            form_data["waiting_days"],
            result["prediction"],
            result["confidence"],
            result.get("risk_level"),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    log_event(app.config["DATABASE"], "INFO", f"Prediction saved: {result['prediction']}")


def register_error_handlers(app: Flask) -> None:
    """Attach friendly error pages for common HTTP errors."""

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        log_event(app.config["DATABASE"], "ERROR", f"Unhandled server error: {error}")
        return render_template("500.html"), 500


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
