import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import get_all_tickets

def render():
    st.markdown("""
    <div class="main-header">
        <h1>📊 IT Helpdesk Dashboard</h1>
        <p>Live overview of all support tickets and team performance</p>
    </div>
    """, unsafe_allow_html=True)

    tickets = get_all_tickets()
    if not tickets:
        st.warning("No ticket data available yet.")
        return

    df = pd.DataFrame([dict(t) for t in tickets])
    df["created_at"]  = pd.to_datetime(df["created_at"])
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")

    # ── KPI METRICS ──────────────────────────────────────────────
    total       = len(df)
    open_t      = len(df[df["status"] == "Open"])
    in_prog     = len(df[df["status"] == "In Progress"])
    resolved    = len(df[df["status"].isin(["Resolved", "Closed"])])

    resolved_df = df[df["resolved_at"].notna()].copy()
    if not resolved_df.empty:
        resolved_df["resolution_hours"] = (
            resolved_df["resolved_at"] - resolved_df["created_at"]
        ).dt.total_seconds() / 3600
        avg_resolution = resolved_df["resolution_hours"].mean()
    else:
        avg_resolution = 0

    critical_open = len(df[(df["priority"] == "Critical") & (df["status"] == "Open")])

    sla_limits    = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}
    open_df       = df[df["status"] == "Open"].copy()
    open_df["age_hours"] = (datetime.now() - open_df["created_at"]).dt.total_seconds() / 3600
    open_df["sla_limit"] = open_df["priority"].map(sla_limits)
    sla_breached  = len(open_df[open_df["age_hours"] > open_df["sla_limit"]])

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    metrics = [
        (col1, str(total),               "Total Tickets"),
        (col2, str(open_t),              "Open"),
        (col3, str(in_prog),             "In Progress"),
        (col4, str(resolved),            "Resolved / Closed"),
        (col5, f"{avg_resolution:.1f}h", "Avg Resolution Time"),
        (col6, str(sla_breached),        "SLA Breaches"),
    ]
    for col, value, label in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{value}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 1: STATUS + PRIORITY ──────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🎯 Tickets by Status")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        color_map = {
            "Open": "#3182ce", "In Progress": "#d69e2e",
            "Resolved": "#38a169", "Closed": "#718096"
        }
        fig = px.pie(
            status_counts, names="Status", values="Count",
            color="Status", color_discrete_map=color_map,
            hole=0.45
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                          legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### 🚦 Tickets by Priority")
        priority_order  = ["Critical", "High", "Medium", "Low"]
        priority_counts = df["priority"].value_counts().reindex(priority_order, fill_value=0).reset_index()
        priority_counts.columns = ["Priority", "Count"]
        pcolor_map = {
            "Critical": "#e53e3e", "High": "#dd6b20",
            "Medium": "#d69e2e",  "Low": "#38a169"
        }
        fig2 = px.bar(
            priority_counts, x="Priority", y="Count",
            color="Priority", color_discrete_map=pcolor_map,
            text="Count"
        )
        fig2.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                           showlegend=False)
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    # ── ROW 2: CATEGORY + VOLUME OVER TIME ────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### 📂 Volume by Category")
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig3 = px.bar(
            cat_counts, x="Count", y="Category",
            orientation="h", color="Count",
            color_continuous_scale="Blues", text="Count"
        )
        fig3.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                           coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        fig3.update_traces(textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("#### 📅 Ticket Volume — Last 30 Days")
        last_30 = df[df["created_at"] >= (datetime.now() - pd.Timedelta(days=30))].copy()
        last_30["date"] = last_30["created_at"].dt.date
        daily = last_30.groupby("date").size().reset_index(name="Count")
        fig4  = px.area(daily, x="date", y="Count", line_shape="spline")
        fig4.update_traces(fill="tozeroy", line_color="#0f3460",
                           fillcolor="rgba(15,52,96,0.15)")
        fig4.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                           xaxis_title="", yaxis_title="Tickets Submitted")
        st.plotly_chart(fig4, use_container_width=True)

    # ── ROW 3: DEPARTMENT BREAKDOWN + ASSIGNEE WORKLOAD ──────────
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("#### 🏢 Tickets by Department")
        dept_counts = df["department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig5 = px.bar(
            dept_counts, x="Department", y="Count",
            color="Department", text="Count"
        )
        fig5.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                           showlegend=False, xaxis_tickangle=-30)
        fig5.update_traces(textposition="outside")
        st.plotly_chart(fig5, use_container_width=True)

    with col_f:
        st.markdown("#### 👩‍💻 IT Staff Workload (Open + In Progress)")
        active = df[df["status"].isin(["Open", "In Progress"])]
        if not active.empty:
            workload = active.groupby("assigned_to").size().reset_index(name="Active Tickets")
            workload = workload[workload["assigned_to"] != "Unassigned"]
            if not workload.empty:
                fig6 = px.bar(
                    workload, x="assigned_to", y="Active Tickets",
                    color="Active Tickets", color_continuous_scale="Oranges",
                    text="Active Tickets"
                )
                fig6.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                                   coloraxis_showscale=False, xaxis_title="IT Staff")
                fig6.update_traces(textposition="outside")
                st.plotly_chart(fig6, use_container_width=True)
            else:
                st.info("All active tickets are currently unassigned.")

    # ── SLA BREACH TABLE ─────────────────────────────────────────
    if sla_breached > 0:
        st.markdown("---")
        st.markdown("#### ⚠️ SLA Breach Alert — Overdue Open Tickets")
        breach_df = open_df[open_df["age_hours"] > open_df["sla_limit"]][[
            "ticket_number", "title", "priority", "department", "assigned_to", "age_hours"
        ]].copy()
        breach_df.columns = ["Ticket #", "Title", "Priority", "Department", "Assigned To", "Age (hrs)"]
        breach_df["Age (hrs)"] = breach_df["Age (hrs)"].round(1)
        st.dataframe(breach_df, use_container_width=True, hide_index=True)
