# CloudStore

> A secure, self-hosted cloud file storage system built with Flask and deployed on Ubuntu Server. A tiny Dropbox-style app that demonstrates the full cloud-computing stack: build, secure, deploy, network.

CloudStore lets users sign up, log in, and upload files into a private per-user bucket. Admins get a separate dashboard to manage every user and every file in the system. The project was built for a **Virtual Cloud Computing (VCC)** course as an end-to-end demonstration of how a real cloud service is put together.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Quick start](#quick-start)
- [Project layout](#project-layout)
- [How it works](#how-it-works)
- [Deploying to an Ubuntu VM](#deploying-to-an-ubuntu-vm)
- [Production stack (Gunicorn + Nginx)](#production-stack-gunicorn--nginx)
- [Security](#security)
- [CLI commands](#cli-commands)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

---

## Features

**For regular users**
- Account signup with bcrypt-hashed passwords
- Personal file dashboard with size, type, and timestamp
- Upload, download, and delete your own files
- Tag files with admin-defined categories
- Storage-used indicator

**For admins**
- System dashboard with user / file / storage counts
- List every user; promote, demote, or delete
- List every file in the system, regardless of owner
- Delete any file
- Create and manage categories
- Cannot accidentally lock themselves out (cannot demote or delete self)

**Under the hood**
- App-factory pattern with three blueprints (`auth`, `files`, `admin`)
- CSRF protection on every form (Flask-WTF)
- Ownership check on every download and delete
- `@role_required("admin")` decorator + blueprint-level guard
- Filenames sanitised + UUID-prefixed before hitting disk
- Per-user storage namespace: `UPLOAD_FOLDER/<user_id>/<uuid>_<name>`
- Relative paths stored in DB (portable across hosts)
- CLI commands for DB init and admin creation

---

## Tech stack

| Layer            | Choice                          |
|------------------|---------------------------------|
| Language         | Python 3.10+ (tested on 3.12)   |
| Web framework    | Flask 3                         |
| ORM              | SQLAlchemy + Flask-SQLAlchemy   |
| Migrations       | Flask-Migrate (Alembic)         |
| Database         | SQLite (dev) → MySQL (prod)     |
| Auth session     | Flask-Login                     |
| Password hashing | bcrypt                          |
| Forms + CSRF     | Flask-WTF + WTForms             |
| Templates        | Jinja2                          |
| Frontend         | Plain HTML + a single stylesheet |
| WSGI (prod)      | Gunicorn                        |
| Reverse proxy    | Nginx                           |
| Target OS        | Ubuntu Server 22.04 LTS         |
| Hypervisor       | VirtualBox                      |

---

## Quick start

### Windows (PowerShell)

```powershell
# 1. Clone
git clone https://github.com/Nehadsys/cloudstore.git
cd cloudstore

# 2. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
Copy-Item .env.example .env
# Edit .env and set SECRET_KEY to a long random string

# 5. Initialise the database and create an admin
$env:FLASK_APP = "run.py"
flask init-db
flask create-admin admin admin@example.com "ChangeMe123!"

# 6. Run the dev server
python run.py
```

Open <http://127.0.0.1:5000> and log in with `admin@example.com` / `ChangeMe123!`.

### Linux / macOS

```bash
git clone https://github.com/Nehadsys/cloudstore.git
cd cloudstore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY
export FLASK_APP=run.py
flask init-db
flask create-admin admin admin@example.com 'ChangeMe123!'
python run.py
```

---

## Project layout

```
cloudstore/
├── app/
│   ├── __init__.py             App factory + CLI commands
│   ├── extensions.py           Shared db, csrf instances
│   ├── models.py               User, File, Category
│   ├── auth/                   signup, login, logout
│   │   ├── forms.py
│   │   └── routes.py
│   ├── files/                  upload, download, delete (user scope)
│   │   └── routes.py
│   ├── admin/                  user / file / category management
│   │   └── routes.py
│   ├── services/storage.py     upload/delete business logic
│   ├── utils/decorators.py     @role_required
│   ├── templates/              Jinja2 (base + auth + files + admin)
│   └── static/style.css        single stylesheet
├── config.py                   Reads .env, exposes Config class
├── run.py                      Entry point: python run.py
├── requirements.txt
├── .env.example                Copy to .env and fill in
├── docs/                       PDF guides + generators
└── scripts/
    └── vm_setup.sh             One-command VM bootstrap
```

---

## How it works

The app follows a layered architecture:

```
Browser  ─►  Flask App  ─►  Extensions (SQLAlchemy / Login / WTF)  ─►  SQLite + Filesystem
```

Every request passes through a series of gates before reaching the view function: **CSRF check → login_required → role_required → ownership check → view**. If any gate fails the request short-circuits with a 4xx.

For full sequence diagrams (login, upload, download with the ownership check), see [`docs/CloudStore_Full_Guide.pdf`](docs/CloudStore_Full_Guide.pdf).

---

## Deploying to an Ubuntu VM

The project is designed to run on an Ubuntu Server VM (VirtualBox or VMware). At a high level:

1. **Install Ubuntu Server 22.04** in VirtualBox; set the network adapter to **Bridged** so the host can reach the VM by IP.
2. **Install OpenSSH on the VM** (`sudo apt install openssh-server`) so you can `scp` files in.
3. **Copy the project across** from your dev machine:
   ```powershell
   scp -r "C:\path\to\cloudstore" user@VM_IP:~/cloudstore
   ```
4. **Run the bootstrap script** on the VM:
   ```bash
   cd ~/cloudstore
   chmod +x scripts/vm_setup.sh
   ./scripts/vm_setup.sh
   ```
   This installs Python, creates a virtualenv, installs dependencies, generates a random `SECRET_KEY`, initialises the database, creates the default admin, and opens the firewall.
5. **Start the server**:
   ```bash
   source .venv/bin/activate
   python run.py
   ```
6. **From your host browser**: open `http://VM_IP:5000`.

---

## Production stack (Gunicorn + Nginx)

For a more realistic production setup, run behind Gunicorn and Nginx:

```bash
# 1. Run with Gunicorn (4 workers, internal port 8000)
gunicorn -w 4 -b 127.0.0.1:8000 run:app

# 2. Make it a systemd service so it survives reboots
sudo systemctl enable --now cloudstore

# 3. Front it with Nginx on port 80
sudo apt install -y nginx
# (see docs/CloudStore_Full_Guide.pdf for the full nginx config)

# 4. Open the firewall
sudo ufw allow 80
```

Switching the DB from SQLite to MySQL:

```ini
# .env
DATABASE_URL=mysql+pymysql://cloudstore:password@localhost/cloudstore
UPLOAD_FOLDER=/var/cloudstore/uploads
```

The full systemd unit and Nginx config live in section 15 of [`docs/CloudStore_Full_Guide.pdf`](docs/CloudStore_Full_Guide.pdf).

---

## Security

| Concern             | Mitigation                                                                                       |
|---------------------|--------------------------------------------------------------------------------------------------|
| Password storage    | bcrypt hashing with per-user salt; plaintext never touches the DB                                |
| Session hijacking   | `HttpOnly` + `SameSite=Lax` cookies                                                              |
| CSRF                | Flask-WTF `CSRFProtect` initialised globally; every form includes a token                        |
| Path traversal      | `werkzeug.utils.secure_filename` + UUID prefix on every uploaded filename                        |
| Insecure direct object reference (IDOR) | Server-side ownership check on every download and delete                           |
| Open redirect       | `next=` query parameter is validated as same-origin before redirecting                           |
| Privilege escalation| Role checked from the DB on every request; admins can't demote or delete themselves              |
| Secrets in source   | All secrets in `.env` (gitignored); `config.py` only reads, never hardcodes                      |

---

## CLI commands

```bash
# Create the database tables (skip migrations for quick setup)
flask init-db

# Create an admin user
flask create-admin <username> <email> <password>

# Standard Flask-Migrate workflow when you're ready
flask db init
flask db migrate -m "describe the change"
flask db upgrade

# Tests + lint (when you add them)
pytest tests/ -v
flake8 app/
```

---

## Documentation

Three PDFs live in [`docs/`](docs/), each aimed at a different audience:

| PDF | For | Pages |
|---|---|---|
| [CloudStore_Basic_Guide.pdf](docs/CloudStore_Basic_Guide.pdf) | Reviewers, teachers, anyone non-technical — plain English with no jargon | ~7 |
| [CloudStore_Documentation.pdf](docs/CloudStore_Documentation.pdf) | Technical reviewer — concise design spec with tables | ~8 |
| [CloudStore_Full_Guide.pdf](docs/CloudStore_Full_Guide.pdf) | Future maintainer / operator — deep dive with architecture, ER, and sequence diagrams | ~16 |

Each PDF is generated from a Python script in the same folder. Re-run any of them after changes:

```powershell
python docs/generate_basic_pdf.py
python docs/generate_pdf.py
python docs/generate_full_pdf.py
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Browser can't reach the VM | NAT adapter (not bridged) | VirtualBox → VM Settings → Network → Bridged Adapter |
| `scp: connection refused` | OpenSSH not installed on VM | `sudo apt install -y openssh-server && sudo systemctl enable --now ssh` |
| `apt: temporary failure resolving` | DNS broken on VM | `echo 'nameserver 8.8.8.8' \| sudo tee /etc/resolv.conf` |
| `'csrf_token' is undefined` in a template | `CSRFProtect` not initialised | Already handled in `app/__init__.py`; pull latest |
| `403` on `/admin/` | User role is `user` not `admin` | `flask create-admin ...` or promote via the UI |
| File upload returns 413 | Exceeds `MAX_CONTENT_LENGTH` | Raise `MAX_CONTENT_LENGTH` in `.env` and restart |
| VM IP changed | DHCP lease rotated | Run `ip a | grep inet` on the VM; update your URL (or reserve a static IP in your router) |

Full troubleshooting catalogue is in section 13 of [`docs/CloudStore_Full_Guide.pdf`](docs/CloudStore_Full_Guide.pdf).

---

## Project status

Working end-to-end on both Windows (dev) and Ubuntu Server (deployed). All features in the original spec are implemented. Optional categories feature is live; file-sharing between users is on the roadmap.

Built as coursework for a Virtual Cloud Computing module.
