"""Build the full CloudStore operator + developer guide as a PDF, with diagrams.

Run from the project root:
    python docs/generate_full_pdf.py

Produces: docs/CloudStore_Full_Guide.pdf
"""
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem,
)
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, Polygon, Group,
)


OUT_PATH = Path(__file__).resolve().parent / "CloudStore_Full_Guide.pdf"

NAVY   = colors.HexColor("#1e293b")
ACCENT = colors.HexColor("#2563eb")
MUTED  = colors.HexColor("#64748b")
CODE_BG = colors.HexColor("#f1f5f9")
ROW_ALT = colors.HexColor("#f8fafc")
GREEN  = colors.HexColor("#16a34a")
RED    = colors.HexColor("#dc2626")
AMBER  = colors.HexColor("#d97706")
BOX_FILL = colors.HexColor("#eff6ff")
BOX_BORDER = colors.HexColor("#93c5fd")
ACTOR_FILL = colors.HexColor("#fef3c7")
ACTOR_BORDER = colors.HexColor("#f59e0b")


# ----------- text styles -----------

def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=30, leading=36, textColor=NAVY, alignment=TA_CENTER, spaceAfter=6),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=14, leading=18, textColor=MUTED, alignment=TA_CENTER, spaceAfter=20),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, textColor=NAVY, spaceBefore=10, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, textColor=ACCENT, spaceBefore=10, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=colors.black, spaceAfter=6, alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=colors.black, spaceAfter=2),
        "code": ParagraphStyle("code", parent=base["Code"], fontName="Courier",
            fontSize=9, leading=12, textColor=NAVY, backColor=CODE_BG,
            leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10, borderPadding=6),
        "caption": ParagraphStyle("caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceAfter=12),
        "note": ParagraphStyle("note", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=14, textColor=NAVY, backColor=colors.HexColor("#fef9c3"),
            leftIndent=8, rightIndent=8, borderPadding=6, spaceAfter=10),
    }


def code_block(text, s):
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(safe, s["code"])


def bullets(items, s):
    return ListFlowable(
        [ListItem(Paragraph(text, s["bullet"]), leftIndent=12) for text in items],
        bulletType="bullet", start="-", leftIndent=14, bulletFontSize=10, bulletOffsetY=-1,
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
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1),
         [colors.white, ROW_ALT]),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl


# ----------- diagram primitives -----------

def box(g, x, y, w, h, title, lines=None, fill=BOX_FILL, border=BOX_BORDER,
        title_color=NAVY, font_size=9):
    g.add(Rect(x, y, w, h, fillColor=fill, strokeColor=border, strokeWidth=1, rx=4, ry=4))
    g.add(String(x + w/2, y + h - 14, title,
                 fontName="Helvetica-Bold", fontSize=font_size + 1,
                 fillColor=title_color, textAnchor="middle"))
    if lines:
        for i, ln in enumerate(lines):
            g.add(String(x + w/2, y + h - 28 - i * (font_size + 3), ln,
                         fontName="Helvetica", fontSize=font_size,
                         fillColor=NAVY, textAnchor="middle"))


def arrow(g, x1, y1, x2, y2, label=None, dashed=False, color=NAVY, label_above=True):
    line = Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1)
    if dashed:
        line.strokeDashArray = [3, 3]
    g.add(line)
    # arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    ah = 7  # arrowhead length
    aw = 4  # arrowhead width
    p1x = x2 - ah * math.cos(angle) + aw * math.sin(angle)
    p1y = y2 - ah * math.sin(angle) - aw * math.cos(angle)
    p2x = x2 - ah * math.cos(angle) - aw * math.sin(angle)
    p2y = y2 - ah * math.sin(angle) + aw * math.cos(angle)
    g.add(Polygon([x2, y2, p1x, p1y, p2x, p2y],
                  fillColor=color, strokeColor=color))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        offset = 6 if label_above else -10
        g.add(String(mx, my + offset, label,
                     fontName="Helvetica", fontSize=8,
                     fillColor=color, textAnchor="middle"))


def actor(g, x, y, name):
    """Stick figure with name underneath."""
    g.add(Polygon([x, y, x-6, y-12, x+6, y-12],
                  fillColor=ACTOR_FILL, strokeColor=ACTOR_BORDER))
    g.add(Rect(x-3, y+2, 6, 6, fillColor=ACTOR_FILL, strokeColor=ACTOR_BORDER))
    g.add(String(x, y - 22, name, fontName="Helvetica-Bold", fontSize=9,
                 fillColor=NAVY, textAnchor="middle"))


# ----------- diagrams -----------

def diagram_topology():
    d = Drawing(450, 220)
    # Host
    box(d, 20, 110, 170, 80, "Windows Host",
        ["192.168.100.3", "", "Browser  |  PowerShell"], fill=colors.HexColor("#dbeafe"))
    # VM
    box(d, 260, 110, 170, 80, "Ubuntu VM (VirtualBox)",
        ["192.168.100.73", "", "Flask :5000  |  sshd :22"], fill=colors.HexColor("#dcfce7"))
    # Bridged adapter
    box(d, 130, 30, 190, 40, "Home LAN / Wi-Fi",
        ["Bridged adapter --> same /24 subnet"], fill=colors.HexColor("#fef3c7"))
    # Lines
    d.add(Line(105, 110, 105, 70, strokeColor=NAVY, strokeWidth=1.2))
    d.add(Line(345, 110, 345, 70, strokeColor=NAVY, strokeWidth=1.2))
    # HTTP arrow
    arrow(d, 190, 150, 260, 150, label="HTTP :5000", color=ACCENT)
    arrow(d, 260, 130, 190, 130, label="response", color=ACCENT, label_above=False)
    return d


def diagram_architecture():
    d = Drawing(450, 290)
    # Browser layer
    box(d, 160, 240, 130, 35, "Web Browser",
        ["(Windows host)"], fill=colors.HexColor("#dbeafe"))
    # Flask layer
    box(d, 50, 145, 350, 65, "Flask Application (run.py -> create_app)",
        ["", "auth_bp     files_bp     admin_bp"], fill=colors.HexColor("#e0e7ff"))
    # Extensions layer
    box(d, 50, 85, 350, 40, "Extensions",
        ["SQLAlchemy  |  Flask-Login  |  Flask-WTF (CSRF)  |  bcrypt"],
        fill=colors.HexColor("#fae8ff"))
    # Storage
    box(d, 50, 10, 160, 55, "SQLite DB",
        ["cloudstore.db", "users / files / categories"], fill=colors.HexColor("#dcfce7"))
    box(d, 240, 10, 160, 55, "Filesystem",
        ["UPLOAD_FOLDER/", "<user_id>/<uuid>_<name>"], fill=colors.HexColor("#fee2e2"))
    # connectors
    arrow(d, 225, 240, 225, 210, color=NAVY)
    arrow(d, 225, 145, 225, 125, color=NAVY)
    arrow(d, 130, 85, 130, 65, color=NAVY)
    arrow(d, 320, 85, 320, 65, color=NAVY)
    return d


def diagram_components():
    d = Drawing(450, 240)
    # Top: factory
    box(d, 160, 195, 130, 35, "create_app()",
        ["app/__init__.py"], fill=colors.HexColor("#e0e7ff"))
    # Blueprints row
    y = 110
    box(d, 20, y, 130, 60, "auth blueprint",
        ["routes.py", "forms.py"], fill=BOX_FILL)
    box(d, 160, y, 130, 60, "files blueprint",
        ["routes.py"], fill=BOX_FILL)
    box(d, 300, y, 130, 60, "admin blueprint",
        ["routes.py"], fill=BOX_FILL)
    # Services / utils row
    box(d, 60, 20, 150, 50, "services/storage.py",
        ["save_upload, delete_file"], fill=colors.HexColor("#fef3c7"))
    box(d, 240, 20, 150, 50, "utils/decorators.py",
        ["role_required"], fill=colors.HexColor("#fef3c7"))
    # arrows
    for x in (85, 225, 365):
        arrow(d, 225, 195, x, 170, color=NAVY)
    arrow(d, 225, 110, 135, 70, color=NAVY)
    arrow(d, 365, 110, 315, 70, color=NAVY)
    arrow(d, 225, 110, 315, 70, color=NAVY)
    return d


def sequence_diagram(actors, messages, height=320):
    """
    actors: list of (label, x)
    messages: list of (from_idx, to_idx, label, dashed)
    """
    d = Drawing(450, height)
    top = height - 30
    bottom = 30
    # Top boxes + lifelines
    for label, x in actors:
        box(d, x - 45, top - 5, 90, 25, label, fill=ACTOR_FILL,
            border=ACTOR_BORDER, font_size=9)
        line = Line(x, top - 5, x, bottom, strokeColor=MUTED, strokeWidth=0.5)
        line.strokeDashArray = [2, 3]
        d.add(line)
    # Messages
    step = (top - 35 - bottom) / max(len(messages), 1)
    for i, (f, t, label, dashed) in enumerate(messages):
        y = top - 45 - i * step
        x1 = actors[f][1]
        x2 = actors[t][1]
        # nudge so arrows don't overlap lifeline endpoints
        if x1 < x2:
            arrow(d, x1 + 2, y, x2 - 2, y, label=label, dashed=dashed,
                  color=ACCENT if not dashed else MUTED)
        else:
            arrow(d, x1 - 2, y, x2 + 2, y, label=label, dashed=dashed,
                  color=ACCENT if not dashed else MUTED)
    return d


def diagram_login():
    actors = [("User", 50), ("Browser", 150), ("Flask", 260), ("DB", 400)]
    msgs = [
        (0, 1, "type email + password", False),
        (1, 2, "POST /auth/login", False),
        (2, 3, "SELECT * FROM users WHERE email=?", False),
        (3, 2, "user row (with hash)", True),
        (2, 2, "bcrypt.checkpw(...)", False),
        (2, 1, "Set-Cookie: session=...; 302 /dashboard", True),
        (1, 0, "show dashboard", True),
    ]
    return sequence_diagram(actors, msgs, height=320)


def diagram_upload():
    actors = [("User", 50), ("Browser", 150), ("Flask", 260), ("DB+FS", 400)]
    msgs = [
        (0, 1, "select file + click Upload", False),
        (1, 2, "POST /upload  (multipart, CSRF token)", False),
        (2, 2, "secure_filename + uuid prefix", False),
        (2, 3, "write bytes to UPLOAD_FOLDER/<uid>/", False),
        (2, 3, "INSERT INTO files(...)", False),
        (3, 2, "ok", True),
        (2, 1, "302 /dashboard + flash", True),
        (1, 0, "see new file in table", True),
    ]
    return sequence_diagram(actors, msgs, height=340)


def diagram_download():
    actors = [("User", 50), ("Browser", 150), ("Flask", 260), ("DB+FS", 400)]
    msgs = [
        (0, 1, "click Download on file row", False),
        (1, 2, "GET /download/<id>", False),
        (2, 3, "SELECT * FROM files WHERE id=?", False),
        (3, 2, "file row (owner_id)", True),
        (2, 2, "if owner_id != me and !is_admin: abort(403)", False),
        (2, 3, "read UPLOAD_FOLDER/<rel_path>", False),
        (3, 2, "bytes", True),
        (2, 1, "200 + Content-Disposition: attachment", True),
        (1, 0, "browser saves file", True),
    ]
    return sequence_diagram(actors, msgs, height=360)


def diagram_er():
    d = Drawing(450, 260)
    # User
    user_lines = ["id  PK", "username  unique", "email  unique",
                  "password_hash", "role  ('user'|'admin')", "created_at"]
    user_h = 18 + 12 * len(user_lines) + 6
    box(d, 20, 240 - user_h, 130, user_h, "User",
        user_lines, fill=colors.HexColor("#dbeafe"))
    # File
    file_lines = ["id  PK", "original_name", "stored_name", "relative_path",
                  "size", "mime_type", "uploaded_at",
                  "owner_id  FK -> User", "category_id  FK -> Category"]
    file_h = 18 + 12 * len(file_lines) + 6
    box(d, 165, 240 - file_h, 150, file_h, "File",
        file_lines, fill=colors.HexColor("#fee2e2"))
    # Category
    cat_lines = ["id  PK", "name  unique"]
    cat_h = 18 + 12 * len(cat_lines) + 6
    box(d, 330, 240 - cat_h, 100, cat_h, "Category",
        cat_lines, fill=colors.HexColor("#dcfce7"))
    # Relations
    d.add(Line(150, 200, 165, 200, strokeColor=NAVY, strokeWidth=1.2))
    d.add(String(157, 205, "1..*", fontName="Helvetica-Oblique", fontSize=8,
                 fillColor=MUTED, textAnchor="middle"))
    d.add(Line(315, 200, 330, 200, strokeColor=NAVY, strokeWidth=1.2))
    d.add(String(322, 205, "*..1", fontName="Helvetica-Oblique", fontSize=8,
                 fillColor=MUTED, textAnchor="middle"))
    return d


def diagram_request_lifecycle():
    d = Drawing(450, 130)
    steps = [
        ("Request", colors.HexColor("#dbeafe")),
        ("CSRF check", colors.HexColor("#fef3c7")),
        ("login_required", colors.HexColor("#fef3c7")),
        ("role_required", colors.HexColor("#fef3c7")),
        ("View func", colors.HexColor("#dcfce7")),
        ("Response", colors.HexColor("#dbeafe")),
    ]
    x = 10
    w = 70
    gap = 5
    for label, color in steps:
        box(d, x, 50, w, 40, label, fill=color, font_size=8)
        if x + w < 440 - 5:
            arrow(d, x + w, 70, x + w + gap, 70, color=NAVY)
        x += w + gap
    d.add(String(225, 25,
                 "Failure at any gate -> early 4xx response (no view executed)",
                 fontName="Helvetica-Oblique", fontSize=9,
                 fillColor=MUTED, textAnchor="middle"))
    return d


# ----------- page chrome -----------

def page_decorations(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.6 * cm, width - 2 * cm, 1.6 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.1 * cm, "CloudStore - Full Operator & Developer Guide")
    canvas.drawRightString(width - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ----------- compose document -----------

def build():
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2.2 * cm,
        title="CloudStore Full Guide",
        author="CloudStore Team",
    )
    s = build_styles()
    story = []

    # ---- Cover ----
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph("CloudStore", s["title"]))
    story.append(Paragraph("Full Operator & Developer Guide", s["subtitle"]))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        "How to bring it back up next time, how every part of the system works, "
        "and how to troubleshoot common problems.",
        s["body"]))
    story.append(Spacer(1, 3 * cm))
    cover_meta = [
        ["Document",  "Full Operator & Developer Guide"],
        ["Version",   "1.0"],
        ["Date",      date.today().strftime("%B %d, %Y")],
        ["Audience",  "Anyone running or modifying CloudStore"],
        ["Companion", "CloudStore_Documentation.pdf (concise design spec)"],
    ]
    story.append(table_simple(cover_meta, col_widths=[4 * cm, 12 * cm], header=False))
    story.append(PageBreak())

    # ---- Table of contents ----
    story.append(Paragraph("Contents", s["h1"]))
    toc_rows = [
        ["1.",  "Quick start (next time)"],
        ["2.",  "What CloudStore is"],
        ["3.",  "Network topology"],
        ["4.",  "System architecture"],
        ["5.",  "Code components"],
        ["6.",  "Data model (ER diagram)"],
        ["7.",  "Request lifecycle"],
        ["8.",  "Login flow (sequence)"],
        ["9.",  "Upload flow (sequence)"],
        ["10.", "Download flow (sequence with auth check)"],
        ["11.", "Admin operations"],
        ["12.", "Day-2 ops (common tasks)"],
        ["13.", "Troubleshooting"],
        ["14.", "Security checklist"],
        ["15.", "Production-style stack (Gunicorn + Nginx)"],
        ["16.", "FAQ"],
    ]
    story.append(table_simple(toc_rows, col_widths=[1.5 * cm, 14 * cm], header=False))
    story.append(PageBreak())

    # ---- 1. Quick start ----
    story.append(Paragraph("1. Quick start (next time you sit down)", s["h1"]))
    story.append(Paragraph(
        "Three scenarios, three sets of commands. Pick the one that matches "
        "where you want the app to run.",
        s["body"]))

    story.append(Paragraph("1a. Just on Windows (dev)", s["h2"]))
    story.append(code_block(
        "cd \"C:\\Users\\dell\\Desktop\\VCC Project\"\n"
        "python run.py\n"
        "# open http://127.0.0.1:5000",
        s))

    story.append(Paragraph("1b. On the Ubuntu VM (already provisioned)", s["h2"]))
    story.append(code_block(
        "# 1. Start the VM in VirtualBox\n"
        "# 2. Log in as nehad\n"
        "cd ~/cloudstore\n"
        "source .venv/bin/activate\n"
        "python run.py\n"
        "# on the Windows host browser, open:\n"
        "#   http://192.168.100.73:5000\n"
        "# (if the VM IP changed, run `ip a | grep inet` first)",
        s))

    story.append(Paragraph("1c. After you change code on Windows, push it to the VM", s["h2"]))
    story.append(code_block(
        "scp -r \"C:\\Users\\dell\\Desktop\\VCC Project\\app\" "
        "nehad@192.168.100.73:~/cloudstore/\n"
        "# the Flask dev server on the VM auto-reloads on file change",
        s))

    story.append(Paragraph(
        "Note: the VM IP is assigned by your home router via DHCP. If you "
        "reboot the VM or your router, the IP may change. Always check with "
        "<font face='Courier'>ip a | grep inet</font> on the VM.",
        s["note"]))

    # ---- 2. What CloudStore is ----
    story.append(Paragraph("2. What CloudStore is", s["h1"]))
    story.append(Paragraph(
        "A small web application for personal file storage. Users sign up, log in, "
        "and upload files into a private bucket. Admins have a separate dashboard "
        "where they can see everything, promote / demote users, and delete content.",
        s["body"]))
    story.append(Paragraph(
        "It runs on Flask. The database is SQLite. File bytes live on the host's "
        "filesystem; only metadata (name, size, owner, category, timestamp) is in "
        "the database. The system is designed to be deployed to a Linux VM that "
        "your Windows host can reach over the LAN.",
        s["body"]))

    # ---- 3. Topology ----
    story.append(Paragraph("3. Network topology", s["h1"]))
    story.append(Paragraph(
        "Your Windows machine and the Ubuntu VM each have their own IP on the "
        "same home network. The VM's network adapter is set to <b>Bridged</b>, "
        "which means VirtualBox places it on the LAN directly rather than "
        "hiding it behind NAT.",
        s["body"]))
    story.append(diagram_topology())
    story.append(Paragraph("Figure 1 - Network topology (Windows host <-> VM over bridged adapter)",
                           s["caption"]))
    story.append(bullets([
        "Host IP: <font face='Courier'>192.168.100.3</font> (your Windows machine)",
        "VM IP:  <font face='Courier'>192.168.100.73</font> (Ubuntu, bridged)",
        "App port: <font face='Courier'>5000</font> (Flask dev server, listens on 0.0.0.0)",
        "SSH port: <font face='Courier'>22</font> (used by <font face='Courier'>scp</font> for file transfer)",
    ], s))

    # ---- 4. Architecture ----
    story.append(PageBreak())
    story.append(Paragraph("4. System architecture", s["h1"]))
    story.append(Paragraph(
        "Top-to-bottom view of one request. The browser talks to Flask; Flask uses "
        "its extensions to read/write the database and the filesystem.",
        s["body"]))
    story.append(diagram_architecture())
    story.append(Paragraph("Figure 2 - Layered architecture", s["caption"]))
    story.append(bullets([
        "<b>Browser</b> - renders HTML, sends form posts with a CSRF token.",
        "<b>Flask app</b> - dispatches the URL to one of three blueprints (auth, files, admin).",
        "<b>Extensions</b> - SQLAlchemy for the DB, Flask-Login for sessions, Flask-WTF for CSRF, bcrypt for passwords.",
        "<b>SQLite DB</b> - rows for users / files / categories.",
        "<b>Filesystem</b> - the raw bytes of every uploaded file, namespaced per user.",
    ], s))

    # ---- 5. Code components ----
    story.append(Paragraph("5. Code components", s["h1"]))
    story.append(Paragraph(
        "The codebase is organised by feature. Each blueprint owns its routes "
        "and (where useful) its forms. Shared concerns sit in <font face='Courier'>"
        "services/</font> and <font face='Courier'>utils/</font>.",
        s["body"]))
    story.append(diagram_components())
    story.append(Paragraph("Figure 3 - Component diagram", s["caption"]))
    story.append(code_block(
        "app/\n"
        "  __init__.py       create_app(), CLI commands\n"
        "  extensions.py     db, csrf, login_manager singletons\n"
        "  models.py         User, File, Category\n"
        "  auth/             signup / login / logout\n"
        "  files/            upload / download / delete (user scope)\n"
        "  admin/            list users, change role, delete user, list files, categories\n"
        "  services/storage.py   save_upload, delete_file\n"
        "  utils/decorators.py   role_required('admin')\n"
        "  templates/        Jinja2 (base + auth + files + admin)\n"
        "  static/style.css  single stylesheet",
        s))

    # ---- 6. ER diagram ----
    story.append(PageBreak())
    story.append(Paragraph("6. Data model (ER diagram)", s["h1"]))
    story.append(Paragraph(
        "Three tables. A user owns many files. A file optionally belongs to a "
        "category. Categories are independent of users.",
        s["body"]))
    story.append(diagram_er())
    story.append(Paragraph("Figure 4 - Entity-relationship diagram", s["caption"]))
    story.append(Paragraph(
        "Key fields explained:",
        s["h3"]))
    story.append(bullets([
        "<b>User.role</b> - <font face='Courier'>'user'</font> or <font face='Courier'>'admin'</font>. "
        "All role checks read this column.",
        "<b>User.password_hash</b> - bcrypt hash with per-user salt. Plain text never touches the DB.",
        "<b>File.relative_path</b> - "
        "<font face='Courier'>&lt;user_id&gt;/&lt;uuid&gt;_&lt;name&gt;</font>. Stored relative to "
        "<font face='Courier'>UPLOAD_FOLDER</font> so the same DB row works on Windows dev and on "
        "the VM under <font face='Courier'>/var/cloudstore/uploads</font>.",
        "<b>File.owner_id</b> - the foreign key every ownership check reads.",
    ], s))

    # ---- 7. Request lifecycle ----
    story.append(Paragraph("7. Request lifecycle", s["h1"]))
    story.append(Paragraph(
        "Every request passes through a series of gates before reaching the view "
        "function. If any gate fails, the request short-circuits with a 4xx and "
        "no business logic runs.",
        s["body"]))
    story.append(diagram_request_lifecycle())
    story.append(Paragraph("Figure 5 - Order of checks", s["caption"]))
    gate_rows = [
        ["Gate", "What it does", "Failure"],
        ["CSRF check", "Flask-WTF verifies the form's csrf_token on every POST.",
         "400 Bad Request"],
        ["login_required", "Flask-Login checks the session cookie.",
         "302 -> /auth/login?next=..."],
        ["role_required", "Custom decorator checks current_user.role.",
         "403 Forbidden"],
        ["Ownership check", "Per-route: file.owner_id == current_user.id (or admin).",
         "403 Forbidden"],
        ["View function", "Runs the actual business logic.",
         "—"],
    ]
    story.append(table_simple(gate_rows, col_widths=[3.5 * cm, 8.5 * cm, 4 * cm]))

    # ---- 8. Login flow ----
    story.append(PageBreak())
    story.append(Paragraph("8. Login flow (sequence)", s["h1"]))
    story.append(diagram_login())
    story.append(Paragraph("Figure 6 - Login sequence", s["caption"]))
    story.append(Paragraph(
        "The password is hashed once at signup with <font face='Courier'>bcrypt.hashpw"
        "</font>. At login time, <font face='Courier'>bcrypt.checkpw</font> hashes "
        "the submitted password with the stored salt and compares in constant time. "
        "On success, Flask-Login signs a session cookie and the browser is "
        "redirected to <font face='Courier'>/dashboard</font>.",
        s["body"]))

    # ---- 9. Upload flow ----
    story.append(Paragraph("9. Upload flow (sequence)", s["h1"]))
    story.append(diagram_upload())
    story.append(Paragraph("Figure 7 - Upload sequence", s["caption"]))
    story.append(Paragraph(
        "Two security steps before the file ever touches disk:", s["h3"]))
    story.append(bullets([
        "<b>secure_filename</b> from werkzeug strips path separators, control "
        "characters, and trailing dots — so <font face='Courier'>../../etc/passwd"
        "</font> becomes <font face='Courier'>etc_passwd</font>.",
        "A <b>UUID hex prefix</b> is prepended so two users (or one user twice) "
        "uploading <font face='Courier'>report.pdf</font> never collide and the "
        "stored name is unguessable.",
    ], s))

    # ---- 10. Download flow ----
    story.append(PageBreak())
    story.append(Paragraph("10. Download flow (sequence with auth check)", s["h1"]))
    story.append(diagram_download())
    story.append(Paragraph("Figure 8 - Download sequence (the highlighted "
                           "ownership check is the security boundary)",
                           s["caption"]))
    story.append(Paragraph(
        "Even if a user guesses another user's file id and types it into the "
        "URL bar, the ownership check returns 403 before any bytes are read.",
        s["body"]))
    story.append(code_block(
        "# app/files/routes.py\n"
        "def _get_owned_file_or_404(file_id):\n"
        "    file = db.session.get(File, file_id)\n"
        "    if file is None:\n"
        "        abort(404)\n"
        "    if file.owner_id != current_user.id and not current_user.is_admin:\n"
        "        abort(403)\n"
        "    return file",
        s))

    # ---- 11. Admin ops ----
    story.append(Paragraph("11. Admin operations", s["h1"]))
    admin_rows = [
        ["Action", "Route", "Notes"],
        ["See system stats",        "GET  /admin/",                     "user count, file count, storage used"],
        ["List all users",          "GET  /admin/users",                "shows role + file count per user"],
        ["Promote / demote",        "POST /admin/users/<id>/role",      "cannot change own role"],
        ["Delete user (and files)", "POST /admin/users/<id>/delete",    "cascade deletes their files on disk too"],
        ["List every file",         "GET  /admin/files",                "shows owner column"],
        ["Delete any file",         "POST /delete/<id>",                "ownership check passes because is_admin"],
        ["Manage categories",       "GET/POST /admin/categories",       "add new tags users can apply at upload"],
    ]
    story.append(table_simple(admin_rows, col_widths=[4 * cm, 5 * cm, 7 * cm]))

    # ---- 12. Day-2 ops ----
    story.append(PageBreak())
    story.append(Paragraph("12. Day-2 ops (common tasks)", s["h1"]))

    story.append(Paragraph("Create a new admin from the CLI", s["h2"]))
    story.append(code_block(
        "# on the VM, with venv activated\n"
        "export FLASK_APP=run.py\n"
        "flask create-admin alice alice@example.com 'StrongPassword!'",
        s))

    story.append(Paragraph("Reset the database (wipe everything)", s["h2"]))
    story.append(code_block(
        "rm cloudstore.db\n"
        "rm -rf uploads/*\n"
        "flask init-db\n"
        "flask create-admin admin admin@example.com 'ChangeMe123!'",
        s))

    story.append(Paragraph("Back up the data", s["h2"]))
    story.append(code_block(
        "tar -czf cloudstore-backup-$(date +%F).tar.gz cloudstore.db uploads/",
        s))

    story.append(Paragraph("Pull the project off the VM (e.g. to share)", s["h2"]))
    story.append(code_block(
        "# from Windows PowerShell\n"
        "scp -r nehad@192.168.100.73:~/cloudstore C:\\Users\\dell\\Desktop\\cloudstore-from-vm",
        s))

    # ---- 13. Troubleshooting ----
    story.append(Paragraph("13. Troubleshooting", s["h1"]))
    tr_rows = [
        ["Symptom", "Likely cause", "Fix"],
        ["Browser can't reach VM IP",
         "Adapter is NAT, not Bridged",
         "VirtualBox -> VM Settings -> Network -> Bridged Adapter"],
        ["SSH 'connection refused'",
         "openssh-server not installed on VM",
         "sudo apt install -y openssh-server && sudo systemctl enable --now ssh"],
        ["apt: 'Temporary failure resolving'",
         "DNS broken on VM",
         "echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf"],
        ["'csrf_token' is undefined in template",
         "CSRFProtect not initialised",
         "Already fixed - app/__init__.py calls csrf.init_app(app)"],
        ["403 on /admin/",
         "User role is 'user', not 'admin'",
         "flask create-admin <username> ... or promote via UI"],
        ["File 413 too large",
         "Upload exceeds MAX_CONTENT_LENGTH",
         "Raise MAX_CONTENT_LENGTH in .env, restart Flask"],
        ["VM IP changed",
         "DHCP lease rotated",
         "Run 'ip a | grep inet' on the VM, update the URL"],
        ["Server still running after Ctrl+C didn't kill it",
         "Background process from earlier session",
         "On Linux: pkill -f 'python run.py'  -  on Windows: stop the PowerShell session"],
    ]
    story.append(table_simple(tr_rows, col_widths=[5 * cm, 5 * cm, 6 * cm]))

    # ---- 14. Security checklist ----
    story.append(PageBreak())
    story.append(Paragraph("14. Security checklist", s["h1"]))
    story.append(Paragraph(
        "Tick these off before showing CloudStore to anyone outside your home "
        "network. The dev server is fine for a classroom or demo; the items "
        "marked <b>production</b> matter only if you put this on the public "
        "internet.",
        s["body"]))
    story.append(bullets([
        "<b>SECRET_KEY</b> is a long random string in <font face='Courier'>.env</font>, not the placeholder.",
        "Default admin password (<font face='Courier'>ChangeMe123!</font>) has been changed.",
        "<font face='Courier'>.env</font> is in <font face='Courier'>.gitignore</font> (it is).",
        "Uploaded files are saved per-user with UUID prefix (they are).",
        "Every download / delete route runs the ownership check (it does).",
        "CSRF protection is global (CSRFProtect.init_app, yes).",
        "<b>(production)</b> Use Gunicorn + Nginx, not the Flask dev server.",
        "<b>(production)</b> Serve over HTTPS with a real certificate.",
        "<b>(production)</b> Switch DB to MySQL or Postgres; back up nightly.",
        "<b>(production)</b> Add rate limiting on /auth/login to slow down brute force.",
    ], s))

    # ---- 15. Gunicorn + Nginx ----
    story.append(Paragraph("15. Production-style stack (Gunicorn + Nginx)", s["h1"]))
    story.append(Paragraph(
        "When you are ready to graduate off the Flask dev server, the recommended "
        "stack is Gunicorn as the WSGI server and Nginx as the reverse proxy on "
        "port 80. This survives a terminal closing and serves static files faster.",
        s["body"]))
    story.append(Paragraph("Install + run Gunicorn", s["h2"]))
    story.append(code_block(
        "source .venv/bin/activate\n"
        "pip install gunicorn  # already in requirements.txt\n"
        "gunicorn -w 4 -b 127.0.0.1:8000 run:app",
        s))

    story.append(Paragraph("Make it a systemd service", s["h2"]))
    story.append(code_block(
        "sudo tee /etc/systemd/system/cloudstore.service > /dev/null <<'EOF'\n"
        "[Unit]\n"
        "Description=CloudStore (Gunicorn)\n"
        "After=network.target\n"
        "\n"
        "[Service]\n"
        "User=nehad\n"
        "WorkingDirectory=/home/nehad/cloudstore\n"
        "Environment=\"PATH=/home/nehad/cloudstore/.venv/bin\"\n"
        "ExecStart=/home/nehad/cloudstore/.venv/bin/gunicorn "
        "-w 4 -b 127.0.0.1:8000 run:app\n"
        "Restart=always\n"
        "\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
        "EOF\n"
        "sudo systemctl daemon-reload\n"
        "sudo systemctl enable --now cloudstore",
        s))

    story.append(Paragraph("Front it with Nginx", s["h2"]))
    story.append(code_block(
        "sudo apt install -y nginx\n"
        "sudo tee /etc/nginx/sites-available/cloudstore > /dev/null <<'EOF'\n"
        "server {\n"
        "  listen 80;\n"
        "  server_name 192.168.100.73;\n"
        "  client_max_body_size 100M;\n"
        "  location / {\n"
        "    proxy_pass http://127.0.0.1:8000;\n"
        "    proxy_set_header Host $host;\n"
        "    proxy_set_header X-Real-IP $remote_addr;\n"
        "  }\n"
        "}\n"
        "EOF\n"
        "sudo ln -sf /etc/nginx/sites-available/cloudstore /etc/nginx/sites-enabled/\n"
        "sudo rm -f /etc/nginx/sites-enabled/default\n"
        "sudo nginx -t && sudo systemctl reload nginx\n"
        "sudo ufw allow 80",
        s))
    story.append(Paragraph(
        "Now open <font face='Courier'>http://192.168.100.73</font> from "
        "Windows (no <font face='Courier'>:5000</font> any more).",
        s["body"]))

    # ---- 16. FAQ ----
    story.append(PageBreak())
    story.append(Paragraph("16. FAQ", s["h1"]))

    story.append(Paragraph("Q. Why two PDFs?", s["h2"]))
    story.append(Paragraph(
        "The other PDF (CloudStore_Documentation.pdf) is the design spec — "
        "concise, good for handing to a reviewer. This one is the operational + "
        "architectural deep dive with diagrams.",
        s["body"]))

    story.append(Paragraph("Q. Can I run only on Windows and skip the VM?", s["h2"]))
    story.append(Paragraph(
        "Yes. <font face='Courier'>python run.py</font> on Windows is fully functional. "
        "The VM exists to mirror a realistic deployment (Linux filesystem layout, "
        "real WSGI server, separate machine over the network) and to satisfy "
        "the project brief.",
        s["body"]))

    story.append(Paragraph("Q. The VM rebooted and the IP changed. Now what?", s["h2"]))
    story.append(Paragraph(
        "Log in to the VM, run <font face='Courier'>ip a | grep inet</font>, "
        "and use the new <font face='Courier'>192.168.x.x</font> address in "
        "the browser. If you want a fixed IP, reserve one in your router's DHCP "
        "settings.",
        s["body"]))

    story.append(Paragraph("Q. How big can an uploaded file be?", s["h2"]))
    story.append(Paragraph(
        "The default cap is 100 MB, set by <font face='Courier'>MAX_CONTENT_LENGTH"
        "</font> in <font face='Courier'>.env</font>. Increase it there and restart "
        "Flask. If you go above ~500 MB, also raise <font face='Courier'>"
        "client_max_body_size</font> in Nginx.",
        s["body"]))

    story.append(Paragraph("Q. How do I add a new feature?", s["h2"]))
    story.append(Paragraph(
        "Add a route to the most relevant blueprint, put any non-trivial logic "
        "in <font face='Courier'>services/</font>, add a template under "
        "<font face='Courier'>app/templates/</font>, and link it from "
        "<font face='Courier'>base.html</font>. Use "
        "<font face='Courier'>@login_required</font> and (for admin features) "
        "<font face='Courier'>@role_required('admin')</font>.",
        s["body"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Generated by <font face='Courier'>docs/generate_full_pdf.py</font>. "
        "Re-run that script whenever the codebase changes.",
        s["caption"]))

    doc.build(story, onFirstPage=page_decorations, onLaterPages=page_decorations)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
