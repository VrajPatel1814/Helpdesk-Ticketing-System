import streamlit as st
from database import init_db, get_user_by_email, get_all_users

st.set_page_config(
    page_title="Plasman IT Helpdesk",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── INIT DB ──────────────────────────────────────────────────────
init_db()

# ── CUSTOM CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }
    .main-header h1 { color: white; font-size: 2.2rem; margin: 0; }
    .main-header p  { color: #a0aec0; margin: 0.5rem 0 0 0; font-size: 1rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #0f3460;
        text-align: center;
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #0f3460; }
    .metric-card .label { font-size: 0.85rem; color: #718096; margin-top: 0.2rem; }
    .priority-critical { background:#fff5f5; border-left:4px solid #e53e3e; border-radius:6px; padding:0.5rem 1rem; }
    .priority-high     { background:#fffaf0; border-left:4px solid #dd6b20; border-radius:6px; padding:0.5rem 1rem; }
    .priority-medium   { background:#fffff0; border-left:4px solid #d69e2e; border-radius:6px; padding:0.5rem 1rem; }
    .priority-low      { background:#f0fff4; border-left:4px solid #38a169; border-radius:6px; padding:0.5rem 1rem; }
    .status-open       { background:#ebf8ff; color:#2b6cb0; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
    .status-inprogress { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
    .status-resolved   { background:#f0fff4; color:#276749; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
    .status-closed     { background:#f7fafc; color:#4a5568; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
    div[data-testid="stButton"] button {
        border-radius: 8px;
        font-weight: 600;
    }
    .ticket-row {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    .login-box {
        max-width: 420px;
        margin: 3rem auto;
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in  = False
    st.session_state.user_name  = ""
    st.session_state.user_email = ""
    st.session_state.user_role  = ""
    st.session_state.user_dept  = ""

# ── LOGIN PAGE ───────────────────────────────────────────────────
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🖥️ Plasman IT Helpdesk</h1>
        <p>Enterprise IT Support Management System</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("### Sign In")
        st.markdown("Select your account to continue")

        users      = get_all_users()
        user_names = [f"{u['name']} ({u['role'].title()})" for u in users]
        selection  = st.selectbox("Select your account", user_names, index=0)

        selected_user = users[user_names.index(selection)]

        st.info(f"📧 {selected_user['email']}  \n🏢 {selected_user['department']}  \n👤 Role: {selected_user['role'].title()}")

        if st.button("Sign In →", use_container_width=True, type="primary"):
            st.session_state.logged_in  = True
            st.session_state.user_name  = selected_user["name"]
            st.session_state.user_email = selected_user["email"]
            st.session_state.user_role  = selected_user["role"]
            st.session_state.user_dept  = selected_user["department"]
            st.rerun()

        st.markdown("---")
        st.caption("💡 **Demo accounts:** Select any employee to submit tickets, or choose an IT admin (Omar Farouk / Fatima Al-Hassan) to access the admin dashboard.")


# ── SIDEBAR ──────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.markdown(f"🏢 {st.session_state.user_dept}")
        st.markdown(f"🔑 {st.session_state.user_role.title()}")
        st.markdown("---")

        if st.session_state.user_role == "admin":
            pages = {
                "📊 Dashboard":      "dashboard",
                "🎫 All Tickets":    "all_tickets",
                "➕ Submit Ticket":  "submit",
                "📋 My Tickets":     "my_tickets",
            }
        else:
            pages = {
                "➕ Submit Ticket":  "submit",
                "📋 My Tickets":     "my_tickets",
                "🔍 Track Ticket":   "track",
            }

        if "current_page" not in st.session_state:
            st.session_state.current_page = list(pages.values())[0]

        for label, page_key in pages.items():
            active = st.session_state.current_page == page_key
            if st.button(label, use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ── MAIN ROUTER ──────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    render_sidebar()

    page = st.session_state.get("current_page", "submit")

    if page == "dashboard" and st.session_state.user_role == "admin":
        from pages.dashboard   import render
    elif page == "all_tickets" and st.session_state.user_role == "admin":
        from pages.all_tickets import render
    elif page == "submit":
        from pages.submit      import render
    elif page == "my_tickets":
        from pages.my_tickets  import render
    elif page == "track":
        from pages.track       import render
    else:
        from pages.submit      import render

    render()


if __name__ == "__main__":
    main()
