# 🏥 Smart Hospital No-Show Prediction & Management System

A full-stack, production-style Machine Learning web application that predicts whether a patient
will **attend** or **miss** ("no-show") a scheduled hospital appointment — giving hospital staff
a chance to intervene before the appointment slot is wasted.

Built entirely with **free, open-source tools** — no paid APIs, no paid hosting required.

---

## 📌 Project Overview

Missed medical appointments cost hospitals staff time, block slots that other patients could
have used, and disrupt care schedules. This project trains and compares four classic Machine
Learning models on a real 110,000+ row dataset of Brazilian outpatient appointments, automatically
selects the best-performing one, and serves it through a full Flask web application with:

- An instant, form-based prediction tool
- An admin dashboard with live stats
- An analytics page with real dataset visualizations
- A searchable, exportable prediction history
- A model comparison page
- Downloadable PDF prediction reports

---

## ✨ Features

- 🔮 **Instant risk prediction** with confidence score and probability breakdown
- 📊 **Live admin dashboard** — total predictions, attend/no-show split, recent activity, real trend chart
- 📈 **Analytics page** — gender, age-group, chronic-condition, SMS-reminder-effect, and monthly attendance charts
- 🕐 **Searchable prediction history** — search, delete, and export to CSV
- 🧠 **Model comparison page** — Accuracy / Precision / Recall / F1 / ROC-AUC across all 4 trained models
- 🔒 **Secure admin authentication** (password hashing via Werkzeug)
- 📄 **Downloadable PDF prediction report** (via ReportLab)
- 🌗 **Dark mode toggle** (persisted per browser)
- 📱 **Fully responsive** — desktop, tablet, and mobile
- ✅ **46-test automated pytest suite** covering validation, ML pipeline, and every route
- 🧩 **Modular, PEP-8-compliant codebase** — no business logic inside `app.py`

---

## 🛠️ Tech Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| Frontend       | HTML5, CSS3, Bootstrap 5, Vanilla JS      |
| Backend        | Python 3, Flask                          |
| Machine Learning | Scikit-learn, Pandas, NumPy, Joblib    |
| Visualization  | Chart.js, Matplotlib                     |
| Database       | SQLite                                   |
| PDF Reports    | ReportLab                                |
| Testing        | Pytest                                   |
| Deployment     | Render (free tier), Gunicorn             |
| Version Control| Git                                      |

---

## 📊 Dataset

**Source:** Kaggle — ["Medical Appointment No Shows"](https://www.kaggle.com/datasets/joniarroba/noshowappointments)

- **110,527** real outpatient appointment records from Brazil
- Columns: PatientId, AppointmentID, Gender, ScheduledDay, AppointmentDay, Age, Neighbourhood,
  Scholarship, Hipertension, Diabetes, Alcoholism, Handcap, SMS_received, No-show
- The app automatically loads `dataset/KaggleV2-May-2016.csv` — just drop the CSV in that folder.

---

## 🤖 Machine Learning Pipeline & Results

Four models were trained and automatically compared on a held-out 20% test split
(110,526 cleaned rows → 88,420 train / 22,106 test):

| Model                | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|----------------------|----------|-----------|--------|----------|---------|
| Logistic Regression  | 0.667    | 0.318     | 0.569  | 0.408    | 0.663   |
| Decision Tree        | 0.605    | 0.311     | 0.786  | 0.445    | 0.717   |
| Random Forest        | 0.621    | 0.313     | 0.736  | 0.440    | 0.720   |
| **Gradient Boosting** ⭐ | **0.601** | **0.310** | **0.798** | **0.447** | **0.722** |

**Gradient Boosting** was automatically selected as the best model, using **F1 Score** as the
selection metric (rather than Accuracy or ROC-AUC alone) — for a no-show *alert* system, catching
actual no-shows (recall) matters as much as being "accurate" overall, and F1 balances both.


## 📂 Folder Structure

```
hospital-no-show-predictor/
│
├── app.py                      # Flask app factory + all routes (thin — logic lives in utils/)
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # + pytest for running the test suite
├── pytest.ini                  # Pytest configuration
├── Procfile                    # Gunicorn start command (Render/Heroku-style)
├── render.yaml                 # Render Blueprint (one-click deploy config)
├── runtime.txt                 # Pinned Python version
├── .env.example                # Environment variable template
├── .gitignore
├── README.md
│
├── dataset/
│   └── KaggleV2-May-2016.csv   # Place the Kaggle CSV here
│
├── model/                      # ML pipeline — never imported by app.py directly except via utils/predictor.py
│   ├── data_cleaning.py        # Load + clean raw CSV
│   ├── feature_engineering.py  # Single source of truth for model features
│   ├── train.py                # Trains & compares all 4 models, saves the best one
│   ├── evaluate.py             # Accuracy / Precision / Recall / F1 / ROC-AUC
│   └── visualize.py            # EDA charts + precomputed analytics stats
│
├── trained_models/             # Output of model/train.py (gitignored — regenerate via training)
│   ├── best_model.pkl
│   ├── scaler.pkl
│   ├── metrics.json
│   └── dataset_stats.json
│
├── utils/                      # Shared app logic (keeps app.py thin)
│   ├── db.py                   # SQLite connection + schema init + admin seeding
│   ├── auth.py                 # Password hashing + @login_required
│   ├── validators.py           # Form/API input validation
│   ├── logger.py                # Application event logging
│   ├── predictor.py             # Loads trained model, runs predictions
│   └── report.py                # PDF report generation
│
├── database/
│   ├── schema.sql               # admin / prediction_history / application_logs tables
│   └── reset_db.py              # Wipe & recreate a clean database
│
├── templates/                   # Jinja2 HTML pages
├── static/
│   ├── css/style.css            # Custom blue/white hospital theme
│   ├── js/main.js               # Dark mode, form UX, all Chart.js visualizations
│   └── images/eda/               # Generated EDA charts
│
├── notebooks/                    # Optional space for exploratory analysis
└── tests/                        # 46-test pytest suite
```

---

## 🚀 Installation & How to Run (Local)

**1. Clone the repository and enter the folder**
```bash
git clone <your-repo-url>
cd hospital-no-show-predictor
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add the dataset**

Download [the Kaggle dataset](https://www.kaggle.com/datasets/joniarroba/noshowappointments)
and place `KaggleV2-May-2016.csv` inside the `dataset/` folder.

**5. Train the ML model**
```bash
python model/train.py
```
**6. Run the app**
```bash
python app.py
```
Visit **http://localhost:5000**

**7. Log in as admin**

| Field    | Value        |
|----------|--------------|
| Username | `admin`      |
| Password | `Admin@123`  |


---

## ☁️ Deployment (Render — Free Tier)

This repo includes a `render.yaml` Blueprint for one-click deployment:

1. Push this repository to GitHub (make sure `dataset/KaggleV2-May-2016.csv` is committed —
   the model needs it to train during the build step).
2. In the [Render Dashboard](https://dashboard.render.com), choose **New → Blueprint** and select
   your repo.
3. Render will automatically:
   - Run `pip install -r requirements.txt && python model/train.py` (trains a fresh model on every deploy)
   - Start the app with `gunicorn app:app`
4. Set the `SECRET_KEY` environment variable (Render can auto-generate one via the Blueprint).

> **Note:** `trained_models/*.pkl` and `database/*.db` are gitignored by design (binary artifacts
> don't belong in source control). This means the model retrains on every deploy, and the SQLite
> database resets on Render's free tier (ephemeral disk) between deploys/restarts. For persistent
> prediction history in production, attach a Render Disk (paid) or point `DATABASE` at an external
> database.

---
