import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from config import Config
from app.extensions import db, csrf


login_manager = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth.routes import auth_bp
    from app.files.routes import files_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("files.dashboard"))
        return redirect(url_for("auth.login"))

    _register_cli(app)
    return app


def _register_cli(app):
    import click
    from app.models import User

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("email")
    @click.argument("password")
    def create_admin(username, email, password):
        """Create an admin user. Usage: flask create-admin <username> <email> <password>"""
        if User.query.filter((User.email == email) | (User.username == username)).first():
            click.echo("A user with that username or email already exists.")
            return
        user = User(username=username, email=email, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created admin '{username}'.")

    @app.cli.command("init-db")
    def init_db():
        """Create all tables (skip migrations for quick local setup)."""
        db.create_all()
        click.echo("Database tables created.")
