from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse

from app.extensions import db
from app.models import User
from app.auth.forms import SignupForm, LoginForm

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("files.dashboard"))

    form = SignupForm()
    if form.validate_on_submit():
        existing = User.query.filter(
            (User.email == form.email.data) | (User.username == form.username.data)
        ).first()
        if existing:
            flash("That username or email is already registered.", "danger")
            return render_template("auth/signup.html", form=form)

        user = User(username=form.username.data, email=form.email.data, role="user")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created — please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("files.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember.data)
        flash(f"Welcome back, {user.username}!", "success")

        next_url = request.args.get("next")
        if next_url and urlparse(next_url).netloc == "":
            return redirect(next_url)
        return redirect(url_for("files.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
