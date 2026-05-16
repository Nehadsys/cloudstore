from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, send_from_directory, abort, current_app,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models import File, Category
from app.services.storage import save_upload, delete_file

files_bp = Blueprint("files", __name__, template_folder="../templates/files")


def _get_owned_file_or_404(file_id: int) -> File:
    file = db.session.get(File, file_id)
    if file is None:
        abort(404)
    if file.owner_id != current_user.id and not current_user.is_admin:
        abort(403)
    return file


@files_bp.route("/dashboard")
@login_required
def dashboard():
    files = (
        File.query.filter_by(owner_id=current_user.id)
        .order_by(File.uploaded_at.desc())
        .all()
    )
    categories = Category.query.order_by(Category.name).all()
    used = sum(f.size for f in files)
    return render_template(
        "files/dashboard.html",
        files=files,
        categories=categories,
        storage_used=used,
    )


@files_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    upload = request.files.get("file")
    if upload is None or upload.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("files.dashboard"))

    raw_cat = request.form.get("category_id") or ""
    category_id = int(raw_cat) if raw_cat.isdigit() else None

    try:
        record = save_upload(current_user, upload, category_id=category_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("files.dashboard"))

    flash(f"Uploaded '{record.original_name}'.", "success")
    return redirect(url_for("files.dashboard"))


@files_bp.route("/download/<int:file_id>")
@login_required
def download(file_id):
    file = _get_owned_file_or_404(file_id)
    directory = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(
        directory,
        file.relative_path,
        as_attachment=True,
        download_name=file.original_name,
    )


@files_bp.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete(file_id):
    file = _get_owned_file_or_404(file_id)
    name = file.original_name
    delete_file(file)
    flash(f"Deleted '{name}'.", "info")

    if current_user.is_admin and request.form.get("from") == "admin":
        return redirect(url_for("admin.files"))
    return redirect(url_for("files.dashboard"))
