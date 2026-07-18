"""
Authentication utility module.

Provides password hashing/verification helpers and a login_required
decorator to protect admin-only routes (dashboard, analytics, history).
"""

from functools import wraps

from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password for storage."""
    return generate_password_hash(plain_password)


def verify_admin(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against a stored hash."""
    return check_password_hash(password_hash, plain_password)


def login_required(view_func):
    """
    Decorator that redirects to the login page if no admin is
    currently authenticated in the session.
    """

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view
