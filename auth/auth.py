from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from models.db import db
from models import User
from utils.experts import refresh_expert_profile


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        title = request.form.get("title", "").strip() or "IAM Community Member"

        if not name or not email or len(password) < 8:
            flash("Enter your name, email, and a password with at least 8 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("That email is already registered.", "error")
        else:
            user = User(name=name, email=email, title=title)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            refresh_expert_profile(user)
            db.session.commit()
            login_user(user)
            flash("Welcome to the ATIKES IAM community.", "success")
            return redirect(url_for("qa.ask_question"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Signed in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("home.home"))
        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Signed out.", "info")
    return redirect(url_for("home.home"))
