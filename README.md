#🖥️ IT Helpdesk Ticketing System

## 🚀 Live Demo
👉 [Help-Desk Ticketing System](https://appdesk-ticketing-system-8ybpxj4j9bceex37w9cijw.streamlit.app)

A full-stack enterprise IT helpdesk management system built with Python and Streamlit.
Simulates real-world IT support workflows including ticket triage, SLA tracking, and performance dashboards.

---

## 📸 Features

### Employee View
- Submit support tickets with category, priority, and description
- View and track all personal tickets with real-time status
- Post comments and communicate with IT staff
- Track any ticket by number

### IT Admin View
- Full ticket management dashboard with 8 live KPIs
- Filter tickets by status, priority, and category
- Assign tickets to IT staff, update status, add resolution notes
- SLA breach alerts for overdue critical tickets

### Dashboard KPIs
| Metric | Description |
|---|---|
| Total Tickets | All tickets in the system (120+ seeded) |
| Open | Tickets awaiting assignment |
| In Progress | Actively being worked on |
| Resolved / Closed | Completed tickets |
| Avg Resolution Time | Mean hours from open to resolve |
| SLA Breaches | Open tickets past their SLA deadline |

---

## 🚀 Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/VrajPatel1814/it-helpdesk-ticketing-system
cd it-helpdesk-ticketing-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## ☁️ Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — live in ~2 minutes

---

## 🗂️ Project Structure

```
it-helpdesk-ticketing-system/
├── app.py              # Main entry point, login, navigation
├── database.py         # SQLite DB, seed data, all queries
├── requirements.txt    # Python dependencies
├── pages/
│   ├── dashboard.py    # Admin KPI dashboard with Plotly charts
│   ├── all_tickets.py  # Admin ticket management + edit panel
│   ├── submit.py       # Employee ticket submission form
│   ├── my_tickets.py   # Employee personal ticket view
│   └── track.py        # Ticket lookup by number
└── data/
    └── helpdesk.db     # SQLite database (auto-created on first run)
```

---

## 🧑‍💼 Demo Accounts

| Name | Role | Department |
|---|---|---|
| Omar Farouk | **IT Admin** | IT |
| Fatima Al-Hassan | **IT Admin** | IT |
| James Carter | Employee | Finance |
| Sarah Mitchell | Employee | HR |
| Priya Sharma | Employee | Operations |
| Kevin Brown | Employee | Engineering |
| *(+ 10 more employees)* | | |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **Charts:** Plotly Express
- **Deployment:** Streamlit Cloud

---

## 📊 Sample Data

The system is pre-loaded with **120 realistic tickets** across:
- 6 categories: Hardware, Software, Network, Access & Permissions, Email, Peripherals
- 4 priority levels with corresponding SLA targets
- 8 departments across 2 site locations
- 90-day historical data for trend analysis
