"""Build the CloudStore beginner-friendly guide.

Run from the project root:
    python docs/generate_basic_pdf.py

Produces: docs/CloudStore_Basic_Guide.pdf
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
    ListFlowable, ListItem,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon


OUT_PATH = Path(__file__).resolve().parent / "CloudStore_Basic_Guide.pdf"

NAVY   = colors.HexColor("#1e293b")
ACCENT = colors.HexColor("#2563eb")
MUTED  = colors.HexColor("#64748b")
SOFT_BG = colors.HexColor("#f8fafc")
USER_FILL = colors.HexColor("#dbeafe")
WEB_FILL  = colors.HexColor("#fef3c7")
APP_FILL  = colors.HexColor("#e0e7ff")
DB_FILL   = colors.HexColor("#dcfce7")
FS_FILL   = colors.HexColor("#fee2e2")
NOTE_BG   = colors.HexColor("#fef9c3")


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=32, leading=38, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=16, leading=22, textColor=MUTED, alignment=TA_CENTER, spaceAfter=20),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=20, leading=24, textColor=NAVY, spaceBefore=14, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor=ACCENT, spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=11.5, leading=17, textColor=colors.black, spaceAfter=8, alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=11.5, leading=17, textColor=colors.black, spaceAfter=3),
        "caption": ParagraphStyle("caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9.5, leading=13, textColor=MUTED, alignment=TA_CENTER, spaceAfter=14),
        "callout": ParagraphStyle("callout", parent=base["BodyText"], fontName="Helvetica",
            fontSize=11, leading=15, textColor=NAVY, backColor=NOTE_BG,
            leftIndent=10, rightIndent=10, borderPadding=8, spaceAfter=12),
    }


def bullets(items, s):
    return ListFlowable(
        [ListItem(Paragraph(t, s["bullet"]), leftIndent=12) for t in items],
        bulletType="bullet", start="-", leftIndent=14, bulletFontSize=10, bulletOffsetY=-1,
    )


def table_simple(rows, col_widths, header=True):
    tbl = Table(rows, colWidths=col_widths, hAlign="LEFT")
    style = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1),
         [colors.white, SOFT_BG]),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 11),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl


def box(g, x, y, w, h, title, sub=None, fill=USER_FILL):
    g.add(Rect(x, y, w, h, fillColor=fill, strokeColor=NAVY, strokeWidth=1, rx=6, ry=6))
    g.add(String(x + w/2, y + h/2 + (4 if sub else -3), title,
                 fontName="Helvetica-Bold", fontSize=11,
                 fillColor=NAVY, textAnchor="middle"))
    if sub:
        g.add(String(x + w/2, y + h/2 - 10, sub,
                     fontName="Helvetica", fontSize=9,
                     fillColor=MUTED, textAnchor="middle"))


def arrow(g, x1, y1, x2, y2, label=None):
    g.add(Line(x1, y1, x2, y2, strokeColor=NAVY, strokeWidth=1.4))
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    ah, aw = 8, 4
    p1x = x2 - ah*math.cos(angle) + aw*math.sin(angle)
    p1y = y2 - ah*math.sin(angle) - aw*math.cos(angle)
    p2x = x2 - ah*math.cos(angle) - aw*math.sin(angle)
    p2y = y2 - ah*math.sin(angle) + aw*math.cos(angle)
    g.add(Polygon([x2, y2, p1x, p1y, p2x, p2y], fillColor=NAVY, strokeColor=NAVY))
    if label:
        g.add(String((x1+x2)/2, (y1+y2)/2 + 8, label,
                     fontName="Helvetica", fontSize=9,
                     fillColor=NAVY, textAnchor="middle"))


def big_picture_diagram():
    d = Drawing(460, 200)
    box(d, 20,  80, 90, 60, "You", "(Browser)", fill=USER_FILL)
    box(d, 145, 80, 100, 60, "Web Page", "(HTML form)", fill=WEB_FILL)
    box(d, 280, 80, 80, 60, "App", "(Flask)", fill=APP_FILL)
    box(d, 380, 130, 70, 50, "Database", "(SQLite)", fill=DB_FILL)
    box(d, 380, 30,  70, 50, "Disk", "(your files)", fill=FS_FILL)
    arrow(d, 110, 110, 145, 110)
    arrow(d, 245, 110, 280, 110)
    arrow(d, 360, 120, 380, 150)
    arrow(d, 360, 100, 380, 60)
    return d


def phases_diagram():
    d = Drawing(460, 160)
    steps = [
        ("1\nDesign",   USER_FILL),
        ("2\nBuild",    WEB_FILL),
        ("3\nTest",     APP_FILL),
        ("4\nDeploy",   DB_FILL),
        ("5\nDocument", FS_FILL),
    ]
    x = 15
    w = 80
    gap = 10
    for label, color in steps:
        d.add(Rect(x, 60, w, 60, fillColor=color, strokeColor=NAVY, strokeWidth=1, rx=8, ry=8))
        line1, line2 = label.split("\n")
        d.add(String(x + w/2, 95, line1, fontName="Helvetica-Bold", fontSize=14,
                     fillColor=NAVY, textAnchor="middle"))
        d.add(String(x + w/2, 78, line2, fontName="Helvetica", fontSize=10,
                     fillColor=NAVY, textAnchor="middle"))
        if x + w + gap < 460:
            arrow(d, x + w, 90, x + w + gap, 90)
        x += w + gap
    return d


def roles_diagram():
    d = Drawing(460, 170)
    box(d, 50, 60, 150, 90, "Regular User", "Can manage their OWN files only", fill=USER_FILL)
    box(d, 260, 60, 150, 90, "Admin User", "Can manage EVERYTHING", fill=FS_FILL)
    # User items
    items_u = ["Sign up", "Log in", "Upload files", "Download own files", "Delete own files"]
    for i, t in enumerate(items_u):
        d.add(String(125, 130 - 12*i - 30, "- " + t, fontName="Helvetica", fontSize=9,
                     fillColor=NAVY, textAnchor="middle"))
    items_a = ["All user actions", "See ALL users", "Promote / demote", "Delete any user", "Delete any file"]
    for i, t in enumerate(items_a):
        d.add(String(335, 130 - 12*i - 30, "- " + t, fontName="Helvetica", fontSize=9,
                     fillColor=NAVY, textAnchor="middle"))
    return d


def page_chrome(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.6*cm, width - 2*cm, 1.6*cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2*cm, 1.1*cm, "CloudStore - Basic Guide")
    canvas.drawRightString(width - 2*cm, 1.1*cm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    doc = SimpleDocTemplate(
        str(OUT_PATH), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2.2*cm,
        title="CloudStore Basic Guide",
        author="CloudStore Team",
    )
    s = build_styles()
    story = []

    # Cover
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("CloudStore", s["title"]))
    story.append(Paragraph("A Beginner's Guide", s["subtitle"]))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph(
        "What this project is, why we built it, and how it works "
        "explained in plain English with no jargon.",
        s["body"]))
    story.append(Spacer(1, 3*cm))
    cover_meta = [
        ["Document", "Beginner's Guide"],
        ["Date", date.today().strftime("%B %d, %Y")],
        ["For",  "Reviewers, teammates, anyone curious"],
    ]
    story.append(table_simple(cover_meta, col_widths=[4*cm, 12*cm], header=False))
    story.append(PageBreak())

    # 1. What is this project?
    story.append(Paragraph("1. What is this project?", s["h1"]))
    story.append(Paragraph(
        "CloudStore is a small website where people can store their personal files online. "
        "Think of it as a tiny version of Google Drive or Dropbox that we built ourselves.",
        s["body"]))
    story.append(Paragraph(
        "Each person creates an account, logs in, and gets a private space where they can "
        "upload, download, and delete their own files. A separate <b>admin account</b> can "
        "see everyone and everything - useful for the person running the service.",
        s["body"]))

    story.append(Paragraph("2. Why did we build it?", s["h1"]))
    story.append(Paragraph(
        "This is a <b>Virtual Cloud Computing (VCC)</b> project. The goal is not just to "
        "write a website - it is to show that we understand how a real cloud service is put "
        "together end to end. To prove that, we did three things:",
        s["body"]))
    story.append(bullets([
        "<b>Built a real working web application</b> - not just slides or diagrams.",
        "<b>Deployed it on a virtual machine</b> - the same idea every cloud provider "
        "(AWS, Azure, Google Cloud) uses behind the scenes.",
        "<b>Made another computer talk to it over the network</b> - just like users would "
        "reach a real cloud service over the internet.",
    ], s))
    story.append(Paragraph(
        "So this single project touches application development, databases, "
        "security, virtualization, and networking - all the building blocks of cloud computing.",
        s["callout"]))

    # 3. Big picture diagram
    story.append(PageBreak())
    story.append(Paragraph("3. The big picture", s["h1"]))
    story.append(Paragraph(
        "Here is what happens when you use the website. You click something in your browser, "
        "your browser sends that request to our app, and the app saves or fetches things "
        "from two places: a database (for information about files) and the disk (for the "
        "actual file content).",
        s["body"]))
    story.append(big_picture_diagram())
    story.append(Paragraph("Figure 1 - The big picture", s["caption"]))
    story.append(bullets([
        "<b>You</b> use a normal web browser - Chrome, Edge, anything.",
        "<b>The web page</b> shows you forms (login, upload, file list).",
        "<b>The app</b> is the brain. It checks who you are and decides what to do.",
        "<b>The database</b> remembers things like usernames, passwords (hashed), and file info.",
        "<b>The disk</b> holds the actual file bytes.",
    ], s))

    # 4. What can you do?
    story.append(Paragraph("4. What can you actually do on the site?", s["h1"]))
    story.append(Paragraph(
        "There are two kinds of accounts. Regular users see only their own stuff. Admins see "
        "everything. The system enforces this on every single click - it is not just buttons "
        "being hidden, the server actively blocks unauthorised requests.",
        s["body"]))
    story.append(roles_diagram())
    story.append(Paragraph("Figure 2 - The two types of accounts", s["caption"]))

    # 5. Walking through it
    story.append(PageBreak())
    story.append(Paragraph("5. A walk through the website", s["h1"]))
    story.append(Paragraph(
        "If you opened the site right now, this is the journey you would take.",
        s["body"]))

    story.append(Paragraph("Step 1 - Sign up", s["h2"]))
    story.append(Paragraph(
        "You visit the site and click <b>Signup</b>. You pick a username, an email, and a "
        "password. The website never stores your password as you typed it - it runs it "
        "through a one-way scrambler called <b>bcrypt</b> and only stores the scrambled "
        "version. Even we cannot read it back.",
        s["body"]))

    story.append(Paragraph("Step 2 - Log in", s["h2"]))
    story.append(Paragraph(
        "You type your email and password. The site scrambles what you typed and compares "
        "it to what is stored. If they match, you are in. The site puts a small "
        "<b>session cookie</b> in your browser so it remembers you on the next click.",
        s["body"]))

    story.append(Paragraph("Step 3 - Upload a file", s["h2"]))
    story.append(Paragraph(
        "You land on your dashboard. You click <b>Choose File</b>, pick something from your "
        "computer, and hit <b>Upload</b>. Two safety things happen before the file lands on "
        "disk:",
        s["body"]))
    story.append(bullets([
        "The filename is <b>cleaned</b> - dangerous characters like slashes or dots are "
        "removed so nobody can use a sneaky filename to escape into other folders.",
        "A <b>random identifier</b> is added to the front of the name so two people uploading "
        "<i>report.pdf</i> never overwrite each other.",
    ], s))

    story.append(Paragraph("Step 4 - Download a file", s["h2"]))
    story.append(Paragraph(
        "You click <b>Download</b> next to a file in your list. Before sending you anything, "
        "the app checks one critical thing: <b>does this file actually belong to you?</b> "
        "If not, it refuses with a 403 error. Admins are the only exception - they can "
        "download any file.",
        s["body"]))

    story.append(Paragraph("Step 5 - Delete a file", s["h2"]))
    story.append(Paragraph(
        "Same protection. You can delete your own files. Admins can delete anyone's. The app "
        "removes the file from disk <i>and</i> the entry from the database in one go.",
        s["body"]))

    # 6. How we built it
    story.append(PageBreak())
    story.append(Paragraph("6. How we built it (our process)", s["h1"]))
    story.append(Paragraph(
        "We worked in five phases. Each phase had a clear goal so we could check progress "
        "as we went.",
        s["body"]))
    story.append(phases_diagram())
    story.append(Paragraph("Figure 3 - Our five project phases", s["caption"]))

    phases_rows = [
        ["Phase", "What we did", "Why it mattered"],
        ["1. Design",
         "Wrote down the requirements: who uses it, what they can do, what data we store.",
         "Stops you wasting time building the wrong thing."],
        ["2. Build",
         "Coded the Flask app, database tables, and HTML pages.",
         "The actual product."],
        ["3. Test",
         "Ran the app on Windows, signed up, uploaded, downloaded, tried bad inputs.",
         "Catch bugs before the demo, not during it."],
        ["4. Deploy",
         "Created an Ubuntu virtual machine, transferred the code, started the server there.",
         "Proves the project works in a realistic cloud-style environment."],
        ["5. Document",
         "Wrote the README and three PDFs (this one, the design spec, and the full guide).",
         "So anyone can pick it up and understand it."],
    ]
    story.append(table_simple(phases_rows, col_widths=[2.5*cm, 7*cm, 6.5*cm]))

    # 7. Why a virtual machine?
    story.append(Paragraph("7. Why use a virtual machine?", s["h1"]))
    story.append(Paragraph(
        "A virtual machine (VM) is a complete computer pretending to live inside your real "
        "computer. We made a VM running <b>Ubuntu Server 22.04</b> inside VirtualBox. The "
        "app runs there, not on Windows.",
        s["body"]))
    story.append(Paragraph(
        "Why bother? Three reasons:",
        s["body"]))
    story.append(bullets([
        "<b>It looks like a real server.</b> Real cloud servers run Linux. By using a Linux VM "
        "we deal with the same filesystem, same package manager, same firewall rules as a "
        "production system.",
        "<b>It is isolated.</b> Whatever we do inside the VM cannot break Windows. We can "
        "delete it and start over without losing anything.",
        "<b>It demonstrates networking.</b> Two separate machines (Windows host and Linux VM) "
        "talking to each other over a LAN is exactly how clients reach real cloud services.",
    ], s))

    # 8. Tools we used
    story.append(PageBreak())
    story.append(Paragraph("8. The tools we used (in plain English)", s["h1"]))
    tool_rows = [
        ["Tool", "What it is", "What it does for us"],
        ["Python",      "A programming language",       "The language the whole app is written in."],
        ["Flask",       "A small web framework",        "Handles requests and responses."],
        ["SQLite",      "A simple file-based database", "Stores users, file info, categories."],
        ["bcrypt",      "A password hashing tool",      "Scrambles passwords so they can never be read back."],
        ["Jinja2",      "A template engine",            "Fills HTML pages with live data."],
        ["VirtualBox",  "Virtual machine software",     "Runs the Ubuntu VM inside Windows."],
        ["Ubuntu Server", "A Linux operating system",   "What the VM runs - our 'cloud server'."],
        ["SSH / SCP",   "Secure remote tools",          "Used to copy files from Windows to the VM."],
    ]
    story.append(table_simple(tool_rows, col_widths=[3.5*cm, 5*cm, 7.5*cm]))

    # 9. What you see on screen
    story.append(Paragraph("9. What the website looks like", s["h1"]))
    story.append(Paragraph(
        "The site is intentionally simple - clean forms, a navigation bar at the top, "
        "and a single stylesheet. Here are the main pages:",
        s["body"]))
    pages_rows = [
        ["Page", "Purpose"],
        ["Login",            "Type email and password to enter."],
        ["Signup",           "Create a new account."],
        ["My files (Dashboard)",
         "See your own files in a table. Upload form sits at the top."],
        ["Admin dashboard",  "Counts of users, files, and total storage used."],
        ["Admin > Users",    "List of all users with promote / delete buttons."],
        ["Admin > All files","List of every file in the system regardless of owner."],
        ["Admin > Categories","Add labels like 'Documents', 'Images' that users can apply at upload."],
    ]
    story.append(table_simple(pages_rows, col_widths=[5*cm, 11*cm]))

    # 10. What about security?
    story.append(Paragraph("10. What about security?", s["h1"]))
    story.append(Paragraph(
        "Security is built in at every level. The short version:",
        s["body"]))
    story.append(bullets([
        "Passwords are <b>hashed with bcrypt</b> - never stored in plain text.",
        "Every form has a <b>CSRF token</b> - stops other websites tricking your browser.",
        "<b>Filenames are sanitised</b> - no tricks with slashes or dots to escape folders.",
        "<b>Every download and delete</b> checks the file belongs to you first.",
        "<b>Admin pages</b> are blocked at the server, not just hidden in the UI.",
        "<b>Secrets</b> (like the session key) live in a .env file, not in the source code.",
    ], s))

    # 11. Summary
    story.append(PageBreak())
    story.append(Paragraph("11. In one paragraph", s["h1"]))
    story.append(Paragraph(
        "We built a small but real cloud file storage website. People sign up, log in, and "
        "upload files into their own private space. Admins manage everyone. We wrote it in "
        "Python with Flask, stored data in a SQLite database, then deployed the whole thing "
        "onto an Ubuntu Server virtual machine running in VirtualBox. The Windows host opens "
        "the site over the local network - exactly the way users reach real cloud services "
        "over the internet. The result is a working demonstration of the core ideas behind "
        "cloud computing: building, deploying, securing, and operating a service that lives "
        "on a server somewhere else.",
        s["body"]))

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Where to learn more", s["h2"]))
    story.append(bullets([
        "<b>CloudStore_Documentation.pdf</b> - the concise design specification.",
        "<b>CloudStore_Full_Guide.pdf</b> - the full operator and developer guide with "
        "diagrams for login, upload, download, and architecture.",
        "<b>README.md</b> - quick setup commands for Windows and Linux.",
    ], s))

    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(
        "Generated by docs/generate_basic_pdf.py. Re-run that script whenever the project changes.",
        s["caption"]))

    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
