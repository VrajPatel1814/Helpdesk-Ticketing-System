import streamlit as st
from database import get_tickets_by_user, get_comments, add_comment

PRIORITY_COLORS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
STATUS_COLORS   = {"Open": "🔵", "In Progress": "🟡", "Resolved": "🟢", "Closed": "⚫"}

def render():
    st.markdown("""
    <div class="main-header">
        <h1>📋 My Tickets</h1>
        <p>View and track all your submitted support requests</p>
    </div>
    """, unsafe_allow_html=True)

    user    = st.session_state.get("user_name", "")
    tickets = get_tickets_by_user(user)

    if not tickets:
        st.info("You haven't submitted any tickets yet.")
        if st.button("➕ Submit your first ticket", type="primary"):
            st.session_state.current_page = "submit"
            st.rerun()
        return

    # Summary counts
    open_count  = sum(1 for t in tickets if t["status"] == "Open")
    prog_count  = sum(1 for t in tickets if t["status"] == "In Progress")
    done_count  = sum(1 for t in tickets if t["status"] in ("Resolved", "Closed"))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="value">{len(tickets)}</div>
        <div class="label">Total Submitted</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="value">{open_count}</div>
        <div class="label">Open</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="value">{prog_count}</div>
        <div class="label">In Progress</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="value">{done_count}</div>
        <div class="label">Resolved / Closed</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if "view_ticket" not in st.session_state:
        st.session_state.view_ticket = None

    for ticket in tickets:
        p_icon = PRIORITY_COLORS.get(ticket["priority"], "⚪")
        s_icon = STATUS_COLORS.get(ticket["status"], "⚪")

        with st.expander(
            f"{ticket['ticket_number']} — {ticket['title']}  |  "
            f"{p_icon} {ticket['priority']}  |  {s_icon} {ticket['status']}",
            expanded=(st.session_state.view_ticket == ticket["ticket_number"])
        ):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Category:** {ticket['category']}")
                st.markdown(f"**Priority:** {p_icon} {ticket['priority']}")
                st.markdown(f"**Status:** {s_icon} {ticket['status']}")
            with col_b:
                st.markdown(f"**Assigned To:** {ticket['assigned_to']}")
                st.markdown(f"**Submitted:** {ticket['created_at']}")
                st.markdown(f"**Last Updated:** {ticket['updated_at']}")

            st.markdown("**Description:**")
            st.info(ticket["description"])

            if ticket["resolution_notes"]:
                st.markdown("**✅ Resolution Notes:**")
                st.success(ticket["resolution_notes"])

            # Comments
            st.markdown("**💬 Comments:**")
            comments = get_comments(ticket["id"])
            if comments:
                for c in comments:
                    with st.chat_message("assistant"):
                        st.markdown(f"**{c['author']}** — *{c['created_at']}*")
                        st.markdown(c["comment"])
            else:
                st.caption("No comments yet. IT staff will post updates here.")

            new_comment = st.text_area("Add a comment", key=f"comment_{ticket['id']}")
            if st.button("Post Comment", key=f"post_{ticket['id']}"):
                if new_comment.strip():
                    add_comment(ticket["id"], st.session_state.user_name, new_comment)
                    st.success("Comment posted.")
                    st.rerun()
