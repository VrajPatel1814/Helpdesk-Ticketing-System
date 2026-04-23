import streamlit as st
from database import get_ticket_by_number

PRIORITY_COLORS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
STATUS_COLORS   = {"Open": "🔵", "In Progress": "🟡", "Resolved": "🟢", "Closed": "⚫"}

def render():
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Track a Ticket</h1>
        <p>Enter a ticket number to check its current status</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ticket_num = st.text_input("Enter Ticket Number", placeholder="e.g. TKT-0042").upper().strip()

        if st.button("🔍 Search", type="primary", use_container_width=True):
            if not ticket_num:
                st.warning("Please enter a ticket number.")
            else:
                ticket = get_ticket_by_number(ticket_num)
                if not ticket:
                    st.error(f"No ticket found with number **{ticket_num}**. Please check and try again.")
                else:
                    p_icon = PRIORITY_COLORS.get(ticket["priority"], "⚪")
                    s_icon = STATUS_COLORS.get(ticket["status"], "⚪")

                    st.markdown("---")
                    st.markdown(f"## {ticket['ticket_number']} — {ticket['title']}")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Category:** {ticket['category']}")
                        st.markdown(f"**Priority:** {p_icon} {ticket['priority']}")
                        st.markdown(f"**Status:** {s_icon} {ticket['status']}")
                        st.markdown(f"**Submitted by:** {ticket['submitted_by']}")
                    with col_b:
                        st.markdown(f"**Department:** {ticket['department']}")
                        st.markdown(f"**Assigned to:** {ticket['assigned_to']}")
                        st.markdown(f"**Created:** {ticket['created_at']}")
                        st.markdown(f"**Last updated:** {ticket['updated_at']}")

                    st.markdown("**Description:**")
                    st.info(ticket["description"])

                    if ticket["resolution_notes"]:
                        st.markdown("**✅ Resolution:**")
                        st.success(ticket["resolution_notes"])

                    sla_map = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}
                    sla_hrs = sla_map.get(ticket["priority"], 24)
                    if ticket["status"] in ("Resolved", "Closed"):
                        st.success(f"✅ This ticket has been **{ticket['status'].lower()}**.")
                    else:
                        st.warning(f"⏳ This ticket is currently **{ticket['status']}**. "
                                   f"SLA target: **{sla_hrs} hours** from submission.")
