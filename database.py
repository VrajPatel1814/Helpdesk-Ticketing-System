import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = "data/helpdesk.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            submitted_by TEXT NOT NULL,
            department TEXT NOT NULL,
            assigned_to TEXT DEFAULT 'Unassigned',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT DEFAULT NULL,
            resolution_notes TEXT DEFAULT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    conn.commit()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()


def seed_data(conn):
    c = conn.cursor()

    users = [
        ("James Carter",     "james.carter@plasman.com",    "Finance",     "employee"),
        ("Sarah Mitchell",   "sarah.mitchell@plasman.com",  "HR",          "employee"),
        ("Omar Farouk",      "omar.farouk@plasman.com",     "IT",          "admin"),
        ("Priya Sharma",     "priya.sharma@plasman.com",    "Operations",  "employee"),
        ("Tom Nguyen",       "tom.nguyen@plasman.com",      "Sales",       "employee"),
        ("Linda Zhao",       "linda.zhao@plasman.com",      "Accounting",  "employee"),
        ("Kevin Brown",      "kevin.brown@plasman.com",     "Engineering", "employee"),
        ("Fatima Al-Hassan", "fatima.alhassan@plasman.com", "IT",          "admin"),
        ("Amy Chen",         "amy.chen@plasman.com",        "Marketing",   "employee"),
        ("David Park",       "david.park@plasman.com",      "Engineering", "employee"),
        ("Rachel Green",     "rachel.green@plasman.com",    "Finance",     "employee"),
        ("Marcus Johnson",   "marcus.johnson@plasman.com",  "Quality",     "employee"),
        ("Julia Thompson",   "julia.thompson@plasman.com",  "HR",          "employee"),
        ("Carlos Rivera",    "carlos.rivera@plasman.com",   "Operations",  "employee"),
        ("Mei Lin",          "mei.lin@plasman.com",         "Finance",     "employee"),
    ]
    c.executemany("INSERT INTO users (name, email, department, role) VALUES (?, ?, ?, ?)", users)

    categories  = ["Hardware", "Software", "Network", "Access & Permissions", "Email", "Peripherals"]
    priorities  = ["Low", "Medium", "High", "Critical"]
    statuses    = ["Open", "In Progress", "Resolved", "Closed"]
    it_staff    = ["Omar Farouk", "Fatima Al-Hassan"]

    titles = {
        "Hardware":             ["Laptop not turning on", "Monitor flickering", "Keyboard not working",
                                 "PC running very slow", "Docking station issues"],
        "Software":             ["MS Teams keeps crashing", "Cannot open Excel file",
                                 "Outlook freezing on startup", "Adobe Reader not responding",
                                 "Windows update failing"],
        "Network":              ["Cannot connect to VPN", "Slow internet on plant floor",
                                 "Wi-Fi dropping frequently", "Cannot access shared drive",
                                 "Network printer offline"],
        "Access & Permissions": ["Cannot log into system", "Need SharePoint folder access",
                                 "Password reset required", "New user account setup",
                                 "Locked out of application"],
        "Email":                ["Emails not sending", "Spam filter blocking emails",
                                 "Cannot access shared mailbox", "Email signature not displaying",
                                 "Outlook profile corrupted"],
        "Peripherals":          ["Printer not printing", "Scanner not detected",
                                 "USB hub not working", "Webcam not recognized",
                                 "Second monitor not detected"],
    }

    descriptions = {
        "Hardware":             "Device is unresponsive. Restart and power checks attempted. Issue persists.",
        "Software":             "Application crashes on launch or after a few minutes of use. Reinstall has not resolved it.",
        "Network":              "User unable to connect to the network resource. Others in the area are unaffected.",
        "Access & Permissions": "User cannot access the required resource. Access was working previously.",
        "Email":                "Email issue reported. IT admin notified and initial investigation is underway.",
        "Peripherals":          "Device not detected. Tried different ports and cables. Driver reinstall may be needed.",
    }

    resolution_options = [
        "Issue resolved by reinstalling drivers and restarting the device.",
        "Root cause identified as misconfigured network settings. Fixed and documented.",
        "User credentials reset and access restored successfully.",
        "Hardware replaced under warranty. User confirmed resolution.",
        "Software patch applied. Issue no longer reproducible.",
        "Escalated to vendor support. Patch applied and verified by user.",
    ]

    dept_map = {u[0]: u[2] for u in users}
    employees = [u[0] for u in users if u[3] == "employee"]
    now = datetime.now()

    tickets = []
    for i in range(1, 121):
        cat      = random.choice(categories)
        priority = random.choices(priorities, weights=[30, 40, 20, 10])[0]
        status   = random.choices(statuses,   weights=[25, 30, 30, 15])[0]
        user     = random.choice(employees)
        dept     = dept_map.get(user, "General")

        created  = now - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        updated  = created + timedelta(hours=random.randint(1, 48))

        resolved_at      = None
        resolution_notes = None
        if status in ("Resolved", "Closed"):
            resolved_at      = (updated + timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S")
            resolution_notes = random.choice(resolution_options)

        tickets.append((
            f"TKT-{str(i).zfill(4)}",
            random.choice(titles[cat]),
            descriptions[cat],
            cat, priority, status, user, dept,
            random.choice(it_staff) if status != "Open" else "Unassigned",
            created.strftime("%Y-%m-%d %H:%M:%S"),
            updated.strftime("%Y-%m-%d %H:%M:%S"),
            resolved_at, resolution_notes
        ))

    c.executemany("""
        INSERT INTO tickets (ticket_number, title, description, category, priority, status,
            submitted_by, department, assigned_to, created_at, updated_at, resolved_at, resolution_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets)
    conn.commit()


# ── TICKET QUERIES ───────────────────────────────────────────────

def get_all_tickets(status_filter=None, priority_filter=None, category_filter=None):
    conn = get_connection()
    query  = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if status_filter   and status_filter   != "All": query += " AND status=?";   params.append(status_filter)
    if priority_filter and priority_filter != "All": query += " AND priority=?"; params.append(priority_filter)
    if category_filter and category_filter != "All": query += " AND category=?"; params.append(category_filter)
    query += " ORDER BY created_at DESC"
    tickets = conn.execute(query, params).fetchall()
    conn.close()
    return tickets

def get_ticket_by_number(ticket_number):
    conn   = get_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE ticket_number=?", (ticket_number,)).fetchone()
    conn.close()
    return ticket

def get_tickets_by_user(name):
    conn    = get_connection()
    tickets = conn.execute(
        "SELECT * FROM tickets WHERE submitted_by=? ORDER BY created_at DESC", (name,)
    ).fetchall()
    conn.close()
    return tickets

def submit_ticket(title, description, category, priority, submitted_by, department):
    conn = get_connection()
    c    = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tickets")
    count         = c.fetchone()[0] + 1
    ticket_number = f"TKT-{str(count).zfill(4)}"
    now           = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO tickets (ticket_number, title, description, category, priority,
            status, submitted_by, department, assigned_to, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'Open', ?, ?, 'Unassigned', ?, ?)
    """, (ticket_number, title, description, category, priority, submitted_by, department, now, now))
    conn.commit()
    conn.close()
    return ticket_number

def update_ticket(ticket_number, status, assigned_to, resolution_notes):
    conn        = get_connection()
    now         = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    resolved_at = now if status in ("Resolved", "Closed") else None
    conn.execute("""
        UPDATE tickets SET status=?, assigned_to=?, resolution_notes=?,
            updated_at=?, resolved_at=?
        WHERE ticket_number=?
    """, (status, assigned_to, resolution_notes, now, resolved_at, ticket_number))
    conn.commit()
    conn.close()

def add_comment(ticket_id, author, comment):
    conn = get_connection()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO comments (ticket_id, author, comment, created_at) VALUES (?, ?, ?, ?)",
        (ticket_id, author, comment, now)
    )
    conn.commit()
    conn.close()

def get_comments(ticket_id):
    conn     = get_connection()
    comments = conn.execute(
        "SELECT * FROM comments WHERE ticket_id=? ORDER BY created_at ASC", (ticket_id,)
    ).fetchall()
    conn.close()
    return comments

def get_all_users():
    conn  = get_connection()
    users = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
    conn.close()
    return users

def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return user
