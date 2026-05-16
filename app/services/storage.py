import os
import uuid
from pathlib import Path
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.extensions import db
from app.models import File, User


def _user_dir(user_id: int) -> Path:
    base = Path(current_app.config["UPLOAD_FOLDER"]) / str(user_id)
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_upload(user: User, upload: FileStorage, category_id: int | None = None) -> File:
    original = secure_filename(upload.filename or "")
    if not original:
        raise ValueError("Invalid filename")

    stored_name = f"{uuid.uuid4().hex}_{original}"
    target_dir = _user_dir(user.id)
    target_path = target_dir / stored_name

    upload.save(str(target_path))
    size = os.path.getsize(target_path)

    relative = f"{user.id}/{stored_name}"

    record = File(
        original_name=original,
        stored_name=stored_name,
        relative_path=relative,
        size=size,
        mime_type=upload.mimetype,
        owner_id=user.id,
        category_id=category_id,
    )
    db.session.add(record)
    db.session.commit()
    return record


def absolute_path(file: File) -> Path:
    return Path(current_app.config["UPLOAD_FOLDER"]) / file.relative_path


def delete_file(file: File) -> None:
    path = absolute_path(file)
    try:
        if path.exists():
            path.unlink()
    finally:
        db.session.delete(file)
        db.session.commit()
