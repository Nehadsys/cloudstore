#!/usr/bin/env bash
# CloudStore VM bootstrap (Ubuntu Server 22.04)
# Run from the project root on the VM after copying the source over.
#
#   chmod +x scripts/vm_setup.sh
#   ./scripts/vm_setup.sh
#
# Idempotent: safe to re-run.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==> Installing system packages (python3, venv, pip)"
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip

if [ ! -d ".venv" ]; then
  echo "==> Creating virtualenv"
  python3 -m venv .venv
fi

echo "==> Installing Python dependencies"
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if [ ! -f ".env" ]; then
  echo "==> Creating .env (random SECRET_KEY)"
  cp .env.example .env
  RANDOM_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  sed -i "s|SECRET_KEY=change-me-to-a-long-random-string|SECRET_KEY=$RANDOM_KEY|" .env
else
  echo "==> .env already exists, leaving it alone"
fi

echo "==> Initialising database"
export FLASK_APP=run.py
flask init-db

if ! flask shell -c "from app.models import User; import sys; sys.exit(0 if User.query.filter_by(role='admin').first() else 1)" >/dev/null 2>&1; then
  echo "==> Creating default admin user (admin@example.com / ChangeMe123!)"
  flask create-admin admin admin@example.com 'ChangeMe123!'
else
  echo "==> An admin user already exists, skipping create-admin"
fi

echo "==> Opening firewall port 5000 (dev server)"
sudo ufw allow 5000 || true

VM_IP="$(hostname -I | awk '{print $1}')"

cat <<EOF

------------------------------------------------------------
CloudStore is ready.

  Activate the venv:    source .venv/bin/activate
  Start the dev server: python run.py

Then on your Windows host, open:

  http://${VM_IP}:5000

Default admin:  admin@example.com  /  ChangeMe123!
(Change this password after first login.)
------------------------------------------------------------
EOF
