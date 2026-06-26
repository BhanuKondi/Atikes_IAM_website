from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user

from models import User
from models.db import db
from utils.admin import admin_required


admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin")


@admin_users_bp.post("/users/<int:user_id>/manage")
@admin_required
def manage_user(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get("action", "")
    if action == "role":
        role = request.form.get("role", "user")
        if role not in {"admin", "user"}:
            flash("Choose a valid role.", "error")
        elif user.id == current_user.id and role != "admin":
            flash("You cannot remove your own admin access.", "error")
        else:
            user.role = role
            db.session.commit()
            flash(f"{user.name}'s access was updated.", "success")
    elif action == "password":
        password = request.form.get("password", "")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        else:
            user.set_password(password)
            db.session.commit()
            flash(f"Password reset for {user.name}.", "success")
    return redirect(url_for("admin_dashboard.dashboard", view="users"))