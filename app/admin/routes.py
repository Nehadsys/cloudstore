from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import User, File, Category
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


@admin_bp.before_request
@login_required
def _require_admin():
    if not current_user.is_admin:
        abort(403)


@admin_bp.route("/")
def dashboard():
    user_count = User.query.count()
    file_count = File.query.count()
    total_bytes = db.session.query(db.func.coalesce(db.func.sum(File.size), 0)).scalar()
    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        file_count=file_count,
        total_bytes=total_bytes,
    )


@admin_bp.route("/users")
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
def change_role(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        flash("You can't change your own role.", "warning")
        return redirect(url_for("admin.users"))

    new_role = request.form.get("role")
    if new_role not in {"user", "admin"}:
        flash("Invalid role.", "danger")
        return redirect(url_for("admin.users"))

    user.role = new_role
    db.session.commit()
    flash(f"{user.username} is now {new_role}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        flash("You can't delete yourself.", "warning")
        return redirect(url_for("admin.users"))

    from app.services.storage import delete_file
    for f in list(user.files):
        delete_file(f)

    db.session.delete(user)
    db.session.commit()
    flash(f"Deleted user '{user.username}'.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/files")
def files():
    all_files = File.query.order_by(File.uploaded_at.desc()).all()
    return render_template("admin/files.html", files=all_files)


@admin_bp.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Name is required.", "warning")
        elif Category.query.filter_by(name=name).first():
            flash("Category already exists.", "warning")
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash(f"Added category '{name}'.", "success")
        return redirect(url_for("admin.categories"))

    cats = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=cats)
