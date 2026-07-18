-- ============================================================
-- Smart Hospital No-Show Prediction & Management System
-- SQLite Database Schema
-- ============================================================

-- Admin users who can log in to view dashboard/history/analytics
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Every prediction made through the app is logged here
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    scholarship INTEGER DEFAULT 0,
    hypertension INTEGER DEFAULT 0,
    diabetes INTEGER DEFAULT 0,
    alcoholism INTEGER DEFAULT 0,
    handicap INTEGER DEFAULT 0,
    sms_received INTEGER DEFAULT 0,
    waiting_days INTEGER DEFAULT 0,
    prediction TEXT NOT NULL,          -- 'Attend' or 'No-Show'
    confidence REAL NOT NULL,          -- 0.0 - 100.0
    risk_level TEXT,                   -- 'Low Risk' / 'High Risk'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Application-level event/error logs
CREATE TABLE IF NOT EXISTS application_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,               -- INFO / WARNING / ERROR
    message TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prediction_created_at ON prediction_history(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON application_logs(created_at);
