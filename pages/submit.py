import streamlit as st
from database import submit_ticket

def render():
    st.markdown("""
    <div class="main-header">
        <h1>➕ Submit a Ticket</h1>
        <p>Report a technical issue and our IT team will respond promptly</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("submit_ticket_form", clear_on_submit=True):
            st.markdown("### 📝 Issue Details")

            title = st.text_input("Issue Title *", placeholder="e.g. Laptop not connecting to VPN")

            category = st.selectbox("Category *", [
                "Hardware", "Software", "Network",
                "Access & Permissions", "Email", "Peripherals"
            ])

            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"],
                help="Low: 72h SLA | Medium: 24h | High: 8h | Critical: 4h")

            priority_guide = {
                "Low":      "✅ **Low** — Minor inconvenience, workaround available (SLA: 72 hours)",
                "Medium":   "🟡 **Medium** — Affecting productivity but not blocking work (SLA: 24 hours)",
                "High":     "🟠 **High** — Blocking work, no workaround available (SLA: 8 hours)",
                "Critical": "🔴 **Critical** — Complete system outage or security incident (SLA: 4 hours)",
            }
            st.info(priority_guide[priority])

            description = st.text_area("Description *",
                placeholder="Please describe the issue in detail. Include:\n"
                            "- What you were doing when the issue occurred\n"
                            "- Any error messages you saw\n"
                            "- Steps you have already tried",
                height=150)

            st.markdown("### 👤 Your Information")
            col_a, col_b = st.columns(2)
            with col_a:
                submitted_by = st.text_input("Your Name *",
                    value=st.session_state.get("user_name", ""), disabled=True)
            with col_b:
                department = st.text_input("Department *",
                    value=st.session_state.get("user_dept", ""), disabled=True)

            submitted = st.form_submit_button("🚀 Submit Ticket", use_container_width=True,
                                              type="primary")

        if submitted:
            if not title or not description:
                st.error("Please fill in the Issue Title and Description.")
            else:
                ticket_number = submit_ticket(
                    title, description, category, priority,
                    submitted_by, department
                )
                st.success(f"✅ Ticket **{ticket_number}** submitted successfully!")
                st.balloons()
                st.info(f"""
                **What happens next:**
                - Your ticket **{ticket_number}** is now in the queue
                - Priority: **{priority}** (SLA: {"4h" if priority == "Critical" else "8h" if priority == "High" else "24h" if priority == "Medium" else "72h"})
                - You'll be notified once an IT technician is assigned
                - Track your ticket status in **My Tickets**
                """)
