# CloudStore

A secure cloud-based file storage system built with Flask. Users sign up, upload and manage their own files; admins manage everything.

See [CLAUDE (2).md](CLAUDE%20(2).md) for the full design spec.

## Quick start (local dev on Windows)

```powershell
# 1. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
Copy-Item .env.example .env
# Edit .env and set SECRET_KEY to a long random string.

# 4. Initialise the database (uses SQLite by default)
$env:FLASK_APP = "run.py"
flask init-db

# 5. Create the first admin user
flask create-admin admin admin@example.com "ChangeMe123!"

# 6. Run the dev server
python run.py
```

Then open http://127.0.0.1:5000.

## Linux / Ubuntu Server

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY
export FLASK_APP=run.py
flask init-db
flask create-admin admin admin@example.com 'ChangeMe123!'
python run.py
```

## Switching to migrations (Flask-Migrate)

Once you want versioned schema changes instead of `flask init-db`:

```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

## Production on the VM (Ubuntu Server 22.04)

```bash
# In .env, point DATABASE_URL at MySQL and set UPLOAD_FOLDER=/var/cloudstore/uploads
sudo mkdir -p /var/cloudstore/uploads
sudo chown -R $USER:$USER /var/cloudstore

# Run with Gunicorn behind Nginx
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

Set the VirtualBox network adapter to **Bridged** so the host browser can reach the VM IP. Open the firewall:

```bash
sudo ufw allow 80      # production via Nginx
# or, for dev:
sudo ufw allow 5000
```

## Project layout

```
cloudstore/
├── app/
│   ├── __init__.py         App factory, blueprint registration, CLI commands
│   ├── extensions.py       Shared SQLAlchemy instance
│   ├── models.py           User, File, Category
│   ├── auth/               Login, signup, logout
│   ├── files/              Upload, download, delete (user-scoped)
│   ├── admin/              Manage users, files, categories
│   ├── services/storage.py Upload/delete business logic
│   ├── utils/decorators.py @role_required
│   ├── templates/          Jinja2 templates
│   └── static/style.css
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── uploads/                Local dev upload root (gitignored)
```

## Security notes

- Passwords are hashed with bcrypt — never stored in plaintext.
- All filenames are sanitised with `werkzeug.utils.secure_filename` and stored as `<user_id>/<uuid>_<original>`.
- File ownership is checked on every download/delete; admins can access any file.
- Forms use Flask-WTF CSRF tokens.
- Secrets live in `.env`, never in `config.py`.

## Running tests / lint

```bash
pytest tests/ -v
flake8 app/
```
