"""Build the CloudStore project documentation PDF.

Run from the project root:
    python docs/generate_pdf.py

Produces: docs/CloudStore_Documentation.pdf
"""
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem,
)


OUT_PATH = Path(__file__).resolve().parent / "CloudStore_Documentation.pdf"

NAVY = colors.HexColor("#1e293b")
ACCENT = colors.HexColor("#2563eb")
MUTED = colors.HexColor("#64748b")
CODE_BG = colors.HexColor("#f1f5f9")
ROW_ALT = colors.HexColor("#f8fafc")


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=28, leading=34, textColor=NAVY, alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=14, leading=18, textColor=MUTED, alignment=TA_CENTER,
            spaceAfter=24,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, textColor=NAVY, spaceBefore=12, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, textColor=ACCENT, spaceBefore=10, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=colors.black, spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=colors.black, spaceAfter=2,
        ),
        "code": ParagraphStyle(
            "code", parent=base["Code"], fontName="Courier",
            fontSize=9, leading=12, textColor=NAVY, backColor=CODE_BG,
            leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10,
            borderPadding=6,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, textColor=MUTED, spaceAfter=10,
        ),
    }
    return styles


def code_block(text, s):
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(safe, s["code"])


def bullets(items, s):
    return ListFlowable(
        [ListItem(Paragraph(text, s["bullet"]), leftIndent=12) for text in items],
        bulletType="bullet",
        start="•",
        leftIndent=14,
        bulletFontSize=10,
        bulletOffsetY=-1,
    )


def table_simple(rows, col_widths, header=True):
    tbl = Table(rows, colWidths=col_widths, hAlign="LEFT")
    style = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl


def page_decorations(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.6 * cm, width - 2 * cm, 1.6 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.1 * cm, "CloudStore — Project Documentation")
    canvas.drawRightString(width - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2.2 * cm,
        title="CloudStore Project Documentation",
        author="CloudStore Team",
    )

    s = build_styles()
    story = []

    # Cover
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("CloudStore", s["title"]))
    story.append(Paragraph("Cloud-Based File Storage System", s["subtitle"]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "A secure web application for personal file storage with admin "
        "oversight, deployed on an Ubuntu Server virtual machine.",
        s["body"]
    ))
    story.append(Spacer(1, 3 * cm))
    cover_meta = [
        ["Document", "Project Documentation"],
        ["Version", "1.0"],
        ["Date", date.today().strftime("%B %d, %Y")],
        ["Audience", "Team members, reviewers, future maintainers"],
    ]
    story.append(table_simple(cover_meta, col_widths=[4 * cm, 10 * cm], header=False))
    story.append(PageBreak())

    # 1. Overview
    story.append(Paragraph("1. Project Overview", s["h1"]))
    story.append(Paragraph(
        "CloudStore is a Flask-based web application that lets authenticated users "
        "upload, download, organise, and delete their own files. It is designed to "
        "run on an Ubuntu Server virtual machine (VirtualBox or VMware) so the "
        "platform mirrors a realistic cloud deployment — host-to-VM networking, "
        "Linux filesystem layout, and a real WSGI server stack in production.",
        s["body"]
    ))
    story.append(Paragraph(
        "The system enforces a two-tier role model. Regular users only ever see "
        "their own files. Administrators have a separate dashboard for managing "
        "every user and every file in the system. Authorisation is enforced at "
        "the route layer — never by hiding buttons in the UI.",
        s["body"]
    ))

    story.append(Paragraph("Key capabilities", s["h2"]))
    story.append(bullets([
        "Account signup and login with bcrypt-hashed passwords",
        "Per-user file upload, download, and delete",
        "File metadata stored in a relational database; raw bytes on the filesystem",
        "Admin dashboard: list all users, promote/demote, delete users and files",
        "Category management (admin-created tags applied at upload time)",
        "CSRF protection on every form (Flask-WTF)",
        "Production-ready deployment path with Gunicorn + Nginx",
    ], s))

    # 2. Tech stack
    story.append(Paragraph("2. Technology Stack", s["h1"]))
    tech_rows = [
        ["Layer", "Choice", "Notes"],
        ["Language", "Python 3.10+", "Tested on 3.12"],
        ["Web framework", "Flask 3", "App-factory pattern, blueprints"],
        ["ORM", "SQLAlchemy + Flask-SQLAlchemy", "Schema in app/models.py"],
        ["Migrations", "Flask-Migrate (Alembic)", "Optional — flask init-db works for quick setup"],
        ["Database", "SQLite (dev) → MySQL (prod)", "Switch via DATABASE_URL"],
        ["Auth session", "Flask-Login", "Login required, remember-me, role gating"],
        ["Password hashing", "bcrypt", "Per-user salt"],
        ["Forms / CSRF", "Flask-WTF + WTForms", "Validation + CSRF tokens"],
        ["Templates", "Jinja2", "No build step"],
        ["Frontend", "Plain HTML/CSS", "Single stylesheet, no JS framework"],
        ["WSGI (prod)", "Gunicorn", "4 workers behind Nginx"],
        ["Config", "python-dotenv", "Secrets in .env, never in config.py"],
    ]
    story.append(table_simple(tech_rows, col_widths=[3.5 * cm, 4.5 * cm, 8 * cm]))

    # 3. Project structure
    story.append(PageBreak())
    story.append(Paragraph("3. Project Structure", s["h1"]))
    story.append(Paragraph(
        "The codebase is organised by feature (blueprint) rather than by file type.",
        s["body"]
    ))
    story.append(code_block(
        "cloudstore/\n"
        "|-- app/\n"
        "|   |-- __init__.py        # App factory + CLI commands\n"
        "|   |-- extensions.py      # Shared db, csrf instances\n"
        "|   |-- models.py          # User, File, Category\n"
        "|   |-- auth/              # signup, login, logout\n"
        "|   |   |-- forms.py\n"
        "|   |   |-- routes.py\n"
        "|   |-- files/             # upload, download, delete (per-user)\n"
        "|   |   |-- routes.py\n"
        "|   |-- admin/             # admin dashboard, user/file mgmt\n"
        "|   |   |-- routes.py\n"
        "|   |-- services/storage.py  # business logic for files on disk\n"
        "|   |-- utils/decorators.py  # @role_required\n"
        "|   |-- templates/         # Jinja2 (base + auth + files + admin)\n"
        "|   |-- static/style.css   # single stylesheet\n"
        "|-- config.py              # Reads .env, exposes Config class\n"
        "|-- run.py                 # Entry point: python run.py\n"
        "|-- requirements.txt\n"
        "|-- .env.example           # Copy to .env and fill in\n"
        "|-- uploads/               # Local dev upload root (gitignored)\n"
        "|-- migrations/            # Created by `flask db init`",
        s
    ))

    # 4. Data model
    story.append(Paragraph("4. Data Model", s["h1"]))
    story.append(Paragraph(
        "Three SQLAlchemy models cover everything the app needs.",
        s["body"]
    ))

    story.append(Paragraph("User", s["h2"]))
    user_rows = [
        ["Field", "Type", "Purpose"],
        ["id", "Integer (PK)", "Primary key"],
        ["username", "String(64), unique", "Display name, must be unique"],
        ["email", "String(120), unique", "Login identifier"],
        ["password_hash", "String(255)", "bcrypt hash — never the raw password"],
        ["role", "String(16)", "'user' or 'admin'"],
        ["created_at", "DateTime", "Account creation timestamp"],
    ]
    story.append(table_simple(user_rows, col_widths=[3.5 * cm, 4 * cm, 8.5 * cm]))

    story.append(Paragraph("File", s["h2"]))
    file_rows = [
        ["Field", "Type", "Purpose"],
        ["id", "Integer (PK)", "Primary key"],
        ["original_name", "String(255)", "Filename as the user uploaded it"],
        ["stored_name", "String(300)", "<uuid>_<sanitised> name on disk"],
        ["relative_path", "String(500)", "<user_id>/<stored_name> — portable across hosts"],
        ["size", "Integer", "Bytes on disk"],
        ["mime_type", "String(100)", "Browser-reported content type"],
        ["uploaded_at", "DateTime", "Upload timestamp (indexed)"],
        ["owner_id", "FK -> users.id", "Required — drives ownership checks"],
        ["category_id", "FK -> categories.id", "Optional"],
    ]
    story.append(table_simple(file_rows, col_widths=[3.5 * cm, 4 * cm, 8.5 * cm]))

    story.append(Paragraph("Category", s["h2"]))
    cat_rows = [
        ["Field", "Type", "Purpose"],
        ["id", "Integer (PK)", "Primary key"],
        ["name", "String(64), unique", "Admin-managed label, e.g. 'Documents'"],
    ]
    story.append(table_simple(cat_rows, col_widths=[3.5 * cm, 4 * cm, 8.5 * cm]))

    # 5. Roles
    story.append(PageBreak())
    story.append(Paragraph("5. Roles & Access Rules", s["h1"]))
    story.append(Paragraph(
        "Every protected route checks two things: that the request is authenticated, "
        "and that the current user is allowed to act on the target resource. The "
        "front-end never makes a security decision on its own.",
        s["body"]
    ))
    role_rows = [
        ["Capability", "user", "admin"],
        ["Sign up / log in", "Yes", "Yes"],
        ["Upload files", "Yes (own bucket)", "Yes"],
        ["Download own files", "Yes", "Yes"],
        ["Download any file", "No", "Yes"],
        ["Delete own files", "Yes", "Yes"],
        ["Delete any file", "No", "Yes"],
        ["List all users", "No", "Yes"],
        ["Promote / demote users", "No", "Yes (cannot demote self)"],
        ["Delete users", "No", "Yes (cannot delete self)"],
        ["Manage categories", "No", "Yes"],
    ]
    story.append(table_simple(role_rows, col_widths=[7 * cm, 4 * cm, 5 * cm]))

    story.append(Paragraph("Enforcement", s["h2"]))
    story.append(bullets([
        "<b>@login_required</b> on every authenticated route.",
        "<b>@role_required('admin')</b> decorator in <font face='Courier'>app/utils/decorators.py</font> for admin-only routes.",
        "Per-request ownership check: <font face='Courier'>file.owner_id != current_user.id and not current_user.is_admin → 403</font>.",
        "Admin blueprint has a <font face='Courier'>before_request</font> guard so even adding a new route can't accidentally leak.",
    ], s))

    # 6. Routes
    story.append(PageBreak())
    story.append(Paragraph("6. Route Map", s["h1"]))
    route_rows = [
        ["Method", "Path", "Purpose"],
        ["GET", "/", "Redirect to dashboard or login"],
        ["GET, POST", "/auth/signup", "Create account"],
        ["GET, POST", "/auth/login", "Log in"],
        ["GET", "/auth/logout", "Log out (login required)"],
        ["GET", "/dashboard", "User's own files + upload form"],
        ["POST", "/upload", "Upload a file"],
        ["GET", "/download/<id>", "Download a file (ownership check)"],
        ["POST", "/delete/<id>", "Delete a file (ownership check)"],
        ["GET", "/admin/", "Admin dashboard (counts, links)"],
        ["GET", "/admin/users", "List all users"],
        ["POST", "/admin/users/<id>/role", "Promote / demote a user"],
        ["POST", "/admin/users/<id>/delete", "Delete a user and their files"],
        ["GET", "/admin/files", "List every file in the system"],
        ["GET, POST", "/admin/categories", "List / create categories"],
    ]
    story.append(table_simple(route_rows, col_widths=[2.5 * cm, 5.5 * cm, 8 * cm]))

    # 7. File handling deep dive
    story.append(Paragraph("7. How File Uploads Work", s["h1"]))
    story.append(Paragraph(
        "File handling is the most security-sensitive part of the application. "
        "The flow below is enforced by <font face='Courier'>app/services/storage.py</font>:",
        s["body"]
    ))
    story.append(bullets([
        "Sanitise the filename with <font face='Courier'>werkzeug.utils.secure_filename</font> — never trust the browser.",
        "Generate a random UUID hex and prepend it to the sanitised name → <font face='Courier'>&lt;uuid&gt;_&lt;original&gt;</font>. This prevents collisions and makes guessing other users' paths effectively impossible.",
        "Save under <font face='Courier'>UPLOAD_FOLDER/&lt;user_id&gt;/&lt;stored_name&gt;</font>. The per-user directory is created on demand.",
        "Persist only the <i>relative</i> path in the DB — so the same DB row works whether the app runs on Windows dev or in <font face='Courier'>/var/cloudstore/uploads</font> on the VM.",
        "Downloads are served via <font face='Courier'>send_from_directory</font> with <font face='Courier'>as_attachment=True</font> and the original filename restored for the user.",
    ], s))

    # 8. Setup
    story.append(PageBreak())
    story.append(Paragraph("8. Local Setup", s["h1"]))
    story.append(Paragraph("Windows (PowerShell)", s["h2"]))
    story.append(code_block(
        "python -m venv .venv\n"
        ".\\.venv\\Scripts\\Activate.ps1\n"
        "pip install -r requirements.txt\n"
        "Copy-Item .env.example .env       # then edit SECRET_KEY\n"
        "$env:FLASK_APP = \"run.py\"\n"
        "flask init-db\n"
        "flask create-admin admin admin@example.com \"ChangeMe123!\"\n"
        "python run.py",
        s
    ))
    story.append(Paragraph("Linux / Ubuntu", s["h2"]))
    story.append(code_block(
        "python3 -m venv .venv\n"
        "source .venv/bin/activate\n"
        "pip install -r requirements.txt\n"
        "cp .env.example .env              # then edit SECRET_KEY\n"
        "export FLASK_APP=run.py\n"
        "flask init-db\n"
        "flask create-admin admin admin@example.com 'ChangeMe123!'\n"
        "python run.py",
        s
    ))
    story.append(Paragraph("Then open http://127.0.0.1:5000.", s["body"]))

    # 9. VM deployment
    story.append(Paragraph("9. VM Deployment", s["h1"]))
    story.append(Paragraph(
        "Target: Ubuntu Server 22.04 LTS in VirtualBox or VMware.",
        s["body"]
    ))
    story.append(bullets([
        "Set the VirtualBox adapter to <b>Bridged</b> so the host browser can reach the VM IP directly.",
        "Create the upload root once: <font face='Courier'>sudo mkdir -p /var/cloudstore/uploads &amp;&amp; sudo chown -R $USER /var/cloudstore</font>",
        "Point <font face='Courier'>UPLOAD_FOLDER</font> in <font face='Courier'>.env</font> at <font face='Courier'>/var/cloudstore/uploads</font>.",
        "Switch <font face='Courier'>DATABASE_URL</font> to MySQL: <font face='Courier'>mysql+pymysql://user:pwd@localhost/cloudstore</font>",
        "Run with Gunicorn: <font face='Courier'>gunicorn -w 4 -b 127.0.0.1:8000 run:app</font>",
        "Front with Nginx as a reverse proxy on port 80.",
        "Firewall: <font face='Courier'>sudo ufw allow 80</font> (prod) or <font face='Courier'>sudo ufw allow 5000</font> (dev only).",
    ], s))

    # 10. Security
    story.append(Paragraph("10. Security Notes", s["h1"]))
    story.append(bullets([
        "Passwords are bcrypt-hashed with a unique salt per user. Plain text never touches the database.",
        "All forms include a CSRF token, enforced globally by <font face='Courier'>CSRFProtect</font>.",
        "Filenames are sanitised before saving — directory traversal and dotfile tricks are blocked.",
        "<font face='Courier'>SESSION_COOKIE_HTTPONLY = True</font> and <font face='Courier'>SAMESITE = 'Lax'</font> to mitigate XSS / CSRF cookie theft.",
        "Secrets live in <font face='Courier'>.env</font> (gitignored), loaded by <font face='Courier'>python-dotenv</font>. <b>Never commit a real <font face='Courier'>.env</font>.</b>",
        "Login redirects validate that <font face='Courier'>next=</font> targets are same-origin — no open redirects.",
        "Admins can't delete or demote themselves — prevents accidental lockout.",
    ], s))

    # 11. Anti-patterns
    story.append(PageBreak())
    story.append(Paragraph("11. Anti-Patterns to Avoid", s["h1"]))
    story.append(bullets([
        "Do NOT store an absolute OS path in the DB — store the relative path from <font face='Courier'>UPLOAD_FOLDER</font>.",
        "Do NOT pass user input straight into <font face='Courier'>os.path.join(UPLOAD_FOLDER, ...)</font>. Always sanitise first.",
        "Do NOT skip the ownership check just because an ID 'isn't exposed in the UI' — IDs are guessable.",
        "Do NOT put secrets into <font face='Courier'>config.py</font>. They belong in <font face='Courier'>.env</font>.",
        "Do NOT rely on hiding admin links in templates as a security measure — gate the routes.",
        "Do NOT use <font face='Courier'>print()</font> for user-facing messages — use <font face='Courier'>flash()</font>.",
    ], s))

    # 12. Future
    story.append(Paragraph("12. Future Work", s["h1"]))
    story.append(bullets([
        "<b>Storage usage stats:</b> per-user quota with a progress bar on the dashboard.",
        "<b>File sharing:</b> generate a signed share token, add a <font face='Courier'>shared_files</font> join table.",
        "<b>Preview pane:</b> inline render images and PDFs without forcing a download.",
        "<b>Two-factor auth:</b> TOTP via <font face='Courier'>pyotp</font> for admin accounts.",
        "<b>Audit log:</b> record every admin action (role change, user delete, file delete) for compliance.",
        "<b>Chunked uploads:</b> support files larger than <font face='Courier'>MAX_CONTENT_LENGTH</font>.",
    ], s))

    # 13. Glossary
    story.append(Paragraph("13. Glossary", s["h1"]))
    glossary_rows = [
        ["Term", "Meaning"],
        ["Blueprint", "Flask's modular grouping of routes — we have one per feature."],
        ["App factory", "<font face='Courier'>create_app()</font> function that builds the Flask app — enables config swaps and easy testing."],
        ["Role gating", "Server-side check that the logged-in user has permission to call a route."],
        ["UUID prefix", "Random 32-char hex prepended to filenames to prevent collisions and guessing."],
        ["WSGI", "The Python web server protocol — Gunicorn speaks it to Nginx."],
    ]
    story.append(table_simple(glossary_rows, col_widths=[4 * cm, 12 * cm]))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Generated automatically from <font face='Courier'>docs/generate_pdf.py</font>. "
        "Re-run that script whenever the source of truth changes.",
        s["caption"]
    ))

    doc.build(story, onFirstPage=page_decorations, onLaterPages=page_decorations)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
