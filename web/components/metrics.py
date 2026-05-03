"""Dashboard metrics and visualization components."""

import streamlit as st


def render_risk_metrics(org_reports: dict):
    """Render risk assessment metrics.

    Args:
        org_reports: Organization reports dictionary
    """
    # Calculate risk scores for each organization
    risk_data = []

    for org_name, report in org_reports.items():
        dep_count = len(report.get("dependencies", {}))
        resource_count = report.get("resource_count", 0)
        can_migrate_standalone = report.get("can_migrate_standalone", False)

        # Risk scoring algorithm
        # Base score
        risk_score = 0

        # Dependencies factor (0-40 points)
        risk_score += min(dep_count * 10, 40)

        # Resource count factor (0-30 points)
        if resource_count > 200:
            risk_score += 30
        elif resource_count > 100:
            risk_score += 20
        elif resource_count > 50:
            risk_score += 10

        # Migration standalone factor (0-30 points)
        if not can_migrate_standalone:
            risk_score += 30

        # Categorize risk
        if risk_score >= 70:
            risk_level = "High"
            color = "🔴"
        elif risk_score >= 40:
            risk_level = "Medium"
            color = "🟡"
        else:
            risk_level = "Low"
            color = "🟢"

        risk_data.append(
            {
                "org": org_name,
                "score": risk_score,
                "level": risk_level,
                "color": color,
                "deps": dep_count,
                "resources": resource_count,
            }
        )

    # Sort by risk score descending
    risk_data.sort(key=lambda x: x["score"], reverse=True)

    # Display risk distribution
    try:
        import plotly.graph_objects as go

        # Create bar chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=[item["org"] for item in risk_data],
                y=[item["score"] for item in risk_data],
                marker_color=[
                    "#EE0000"
                    if item["level"] == "High"
                    else "#FFAA00"
                    if item["level"] == "Medium"
                    else "#00AA00"
                    for item in risk_data
                ],
                text=[f"{item['score']}" for item in risk_data],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Risk Score: %{y}<br>Dependencies: %{customdata[0]}<br>Resources: %{customdata[1]}<extra></extra>",
                customdata=[[item["deps"], item["resources"]] for item in risk_data],
            )
        )

        fig.update_layout(
            title="Risk Score by Organization",
            xaxis_title="Organization",
            yaxis_title="Risk Score (0-100)",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.info("Install plotly for enhanced visualizations")

    # Risk breakdown
    col1, col2, col3 = st.columns(3)

    high_risk = [item for item in risk_data if item["level"] == "High"]
    medium_risk = [item for item in risk_data if item["level"] == "Medium"]
    low_risk = [item for item in risk_data if item["level"] == "Low"]

    with col1:
        st.metric("🔴 High Risk", len(high_risk))
        if high_risk:
            with st.expander("View"):
                for item in high_risk:
                    st.markdown(f"- {item['org']} (Score: {item['score']})")

    with col2:
        st.metric("🟡 Medium Risk", len(medium_risk))
        if medium_risk:
            with st.expander("View"):
                for item in medium_risk:
                    st.markdown(f"- {item['org']} (Score: {item['score']})")

    with col3:
        st.metric("🟢 Low Risk", len(low_risk))
        if low_risk:
            with st.expander("View"):
                for item in low_risk:
                    st.markdown(f"- {item['org']} (Score: {item['score']})")


def render_resource_breakdown(org_reports: dict):
    """Render resource distribution breakdown.

    Args:
        org_reports: Organization reports dictionary
    """
    try:
        import plotly.graph_objects as go

        # Aggregate resource counts
        org_names = []
        resource_counts = []

        for org_name, report in org_reports.items():
            org_names.append(org_name)
            resource_counts.append(report.get("resource_count", 0))

        # Create pie chart
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=org_names,
                    values=resource_counts,
                    hole=0.3,
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>Resources: %{value}<br>%{percent}<extra></extra>",
                )
            ]
        )

        fig.update_layout(title="Resource Distribution by Organization", height=400)

        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        # Fallback to simple table
        import pandas as pd

        data = []
        for org_name, report in org_reports.items():
            data.append({"Organization": org_name, "Resources": report.get("resource_count", 0)})

        df = pd.DataFrame(data)
        df = df.sort_values("Resources", ascending=False)

        st.dataframe(df, use_container_width=True, hide_index=True)

    # Top resource consumers
    st.markdown("#### Top Resource Consumers")

    resource_list = [(org, report.get("resource_count", 0)) for org, report in org_reports.items()]
    resource_list.sort(key=lambda x: x[1], reverse=True)

    col1, col2, col3 = st.columns(3)

    if len(resource_list) > 0:
        with col1:
            st.metric(f"1. {resource_list[0][0]}", f"{resource_list[0][1]} resources")

    if len(resource_list) > 1:
        with col2:
            st.metric(f"2. {resource_list[1][0]}", f"{resource_list[1][1]} resources")

    if len(resource_list) > 2:
        with col3:
            st.metric(f"3. {resource_list[2][0]}", f"{resource_list[2][1]} resources")
