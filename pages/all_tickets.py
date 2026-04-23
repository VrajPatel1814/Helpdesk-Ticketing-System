import streamlit as st
import pandas as pd
from database import get_all_tickets, get_ticket_by_number, update_ticket, add_comment, get_comments

PRIORITY_COLORS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
STATUS_COLORS   = {"Open": "🔵", "In Progress": "🟡", "Resolved": "🟢", "Closed": "⚫"}

def render():
    st.markdown("""
    <div class="main-header">
        <h1>🎫 All Tickets</h1>
        <p>Manage and resolve all helpdesk tickets</p>
    </div>
    """, unsafe_allow_html=True)

    # ── FILTERS ──────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_f   = st.selectbox("Status",   ["All", "Open", "In Progress", "Resolved", "Closed"])
    with col2:
        priority_f = st.selectbox("Priority", ["All", "Critical", "High", "Medium", "Low"])
    with col3:
        category_f = st.selectbox("Category", ["All", "Hardware", "Software", "Network",
                                                "Access & Permissions", "Email", "Peripherals"])
    with col4:
        search     = st.text_input("🔍 Search ticket # or keyword", "")

    tickets = get_all_tickets(
        status_filter=status_f if status_f != "All" else None,
        priority_filter=priority_f if priority_f != "All" else None,
        category_filter=category_f if category_f != "All" else None,
    )

    if search:
        tickets = [t for t in tickets if
                   search.lower() in t["ticket_number"].lower() or
                   search.lower() in t["title"].lower() or
                   search.lower() in t["submitted_by"].lower()]

    st.markdown(f"**{len(tickets)} ticket(s) found**")
    st.markdown("---")

    if not tickets:
        st.info("No tickets match the selected filters.")
        return

    # ── TICKET LIST ───────────────────────────────────────────────
    if "selected_ticket" not in st.session_state:
        st.session_state.selected_ticket = None

    for ticket in tickets:
        p_icon = PRIORITY_COLORS.get(ticket["priority"], "⚪")
        s_icon = STATUS_COLORS.get(ticket["status"], "⚪")

        col_a, col_b, col_c, col_d, col_e, col_f = st.columns([1.2, 3, 1.2, 1.2, 1.5, 1])
        with col_a: st.markdown(f"**{ticket['ticket_number']}**")
        with col_b: st.markdown(f"{ticket['title']}")
        with col_c: st.markdown(f"{p_icon} {ticket['priority']}")
        with col_d: st.markdown(f"{s_icon} {ticket['status']}")
        with col_e: st.markdown(f"👤 {ticket['submitted_by']}")
        with col_f:
            if st.button("Manage", key=f"btn_{ticket['ticket_number']}"):
                st.session_state.selected_ticket = ticket["ticket_number"]
                st.rerun()

        st.divider()

    # ── TICKET DETAIL / EDIT PANEL ────────────────────────────────
    if st.session_state.selected_ticket:
        ticket = get_ticket_by_number(st.session_state.selected_ticket)
        if ticket:
            st.markdown("---")
            st.markdown(f"## 🎫 {ticket['ticket_number']} — {ticket['title']}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Category:** {ticket['category']}")
                st.markdown(f"**Priority:** {PRIORITY_COLORS.get(ticket['priority'],'')} {ticket['priority']}")
                st.markdown(f"**Status:** {STATUS_COLORS.get(ticket['status'],'')} {ticket['status']}")
                st.markdown(f"**Submitted by:** {ticket['submitted_by']} ({ticket['department']})")
            with col2:
                st.markdown(f"**Assigned to:** {ticket['assigned_to']}")
                st.markdown(f"**Created:** {ticket['created_at']}")
                st.markdown(f"**Last updated:** {ticket['updated_at']}")
                if ticket["resolved_at"]:
                    st.markdown(f"**Resolved:** {ticket['resolved_at']}")

            st.markdown("**Description:**")
            st.info(ticket["description"])

            if ticket["resolution_notes"]:
                st.markdown("**Resolution Notes:**")
                st.success(ticket["resolution_notes"])

            # Update form
            st.markdown("### ✏️ Update Ticket")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                new_status = st.selectbox("Update Status",
                    ["Open", "In Progress", "Resolved", "Closed"],
                    index=["Open", "In Progress", "Resolved", "Closed"].index(ticket["status"]))
            with col_u2:
                new_assigned = st.selectbox("Assign To",
                    ["Unassigned", "Omar Farouk", "Fatima Al-Hassan"],
                    index=["Unassigned", "Omar Farouk", "Fatima Al-Hassan"].index(
                        ticket["assigned_to"]) if ticket["assigned_to"] in
                        ["Unassigned", "Omar Farouk", "Fatima Al-Hassan"] else 0)

            new_notes = st.text_area("Resolution Notes", value=ticket["resolution_notes"] or "")

            col_save, col_close = st.columns(2)
            with col_save:
                if st.button("💾 Save Changes", type="primary", use_container_width=True):
                    update_ticket(ticket["ticket_number"], new_status, new_assigned, new_notes)
                    st.success("✅ Ticket updated successfully!")
                    st.rerun()
            with col_close:
                if st.button("✖ Close Panel", use_container_width=True):
                    st.session_state.selected_ticket = None
                    st.rerun()

            # Comments
            st.markdown("### 💬 Comments")
            comments = get_comments(ticket["id"])
            if comments:
                for c in comments:
                    with st.chat_message("assistant"):
                        st.markdown(f"**{c['author']}** — *{c['created_at']}*")
                        st.markdown(c["comment"])
            else:
                st.caption("No comments yet.")

            new_comment = st.text_area("Add a comment", key="new_comment_input")
            if st.button("Post Comment", type="primary"):
                if new_comment.strip():
                    add_comment(ticket["id"], st.session_state.user_name, new_comment)
                    st.success("Comment posted.")
                    st.rerun()
