"""Dashboard Page - Risk metrics and visualization."""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.components.metrics import render_resource_breakdown, render_risk_metrics
from web.utils.session import init_session_state, is_connected

# Initialize session
init_session_state()

# Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Risk Assessment Dashboard")
st.markdown("---")

# Check connection
if not is_connected():
    st.warning("⚠️ Not connected to AAP. Please connect in the main page.")
    st.stop()

# Check if analysis data exists
if not st.session_state.analysis_data:
    st.warning("⚠️ No analysis data available. Please run analysis first.")
    st.info("👉 Go to **Analysis** page and click 'Run Analysis'")
    st.stop()

data = st.session_state.analysis_data

# Only show for global analysis
if data.get("type") != "global":
    st.warning("⚠️ Dashboard is only available for global (all organizations) analysis.")
    st.info("👉 Go to **Analysis** page and run analysis with 'All Organizations' mode")
    st.stop()

# Key metrics
st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

org_reports = data.get("org_reports", {})
total_orgs = data.get("total_organizations", 0)
independent_count = len(data.get("independent_orgs", []))
dependent_count = len(data.get("dependent_orgs", []))

# Calculate total resources
total_resources = sum(report.get("resource_count", 0) for report in org_reports.values())

# Calculate total dependencies
total_dependencies = sum(len(report.get("dependencies", {})) for report in org_reports.values())

with col1:
    st.metric("Total Organizations", total_orgs)

with col2:
    st.metric(
        "Independent",
        independent_count,
        delta=f"{round(independent_count/total_orgs*100) if total_orgs else 0}%",
        delta_color="normal",
    )

with col3:
    st.metric(
        "Dependent",
        dependent_count,
        delta=f"{round(dependent_count/total_orgs*100) if total_orgs else 0}%",
        delta_color="inverse",
    )

with col4:
    st.metric("Total Resources", total_resources)

with col5:
    st.metric("Cross-Org Dependencies", total_dependencies)

st.markdown("---")

# Risk scoring
st.markdown("### ⚠️ Risk Analysis")

# Calculate risk scores
render_risk_metrics(org_reports)

st.markdown("---")

# Resource breakdown
st.markdown("### 📦 Resource Distribution")

render_resource_breakdown(org_reports)

st.markdown("---")

# Organization comparison
st.markdown("### 🏢 Organization Comparison")

import pandas as pd

# Create dataframe for comparison
comparison_data = []
for org_name, report in org_reports.items():
    comparison_data.append(
        {
            "Organization": org_name,
            "Resources": report.get("resource_count", 0),
            "Dependencies": len(report.get("dependencies", {})),
            "Can Migrate Standalone": "✅ Yes" if report.get("can_migrate_standalone") else "❌ No",
            "Required Before": ", ".join(report.get("required_migrations_before", [])) or "None",
        }
    )

df = pd.DataFrame(comparison_data)

# Sort by resources descending
df = df.sort_values("Resources", ascending=False)

st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# Dependency heatmap
st.markdown("### 🔥 Dependency Heatmap")

try:
    import numpy as np
    import plotly.graph_objects as go

    # Build dependency matrix
    org_names = list(org_reports.keys())
    n = len(org_names)
    matrix = np.zeros((n, n))

    for i, org_name in enumerate(org_names):
        report = org_reports[org_name]
        deps = report.get("dependencies", {})
        for dep_org in deps:
            if dep_org in org_names:
                j = org_names.index(dep_org)
                matrix[i][j] = len(deps[dep_org])

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=org_names,
            y=org_names,
            colorscale="Reds",
            text=matrix.astype(int),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
        )
    )

    fig.update_layout(
        title="Organization Dependency Matrix",
        xaxis_title="Depends On →",
        yaxis_title="Organization ↓",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

except ImportError:
    st.info("Install plotly for heatmap visualization: pip install plotly")

st.markdown("---")

# Migration complexity
st.markdown("### 🎯 Migration Complexity Factors")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**High Complexity Indicators:**")
    st.markdown("- Multiple cross-org dependencies")
    st.markdown("- Large resource count (>200)")
    st.markdown("- Deep dependency chains")
    st.markdown("- Circular dependencies (if any)")

with col2:
    st.markdown("**Low Complexity Indicators:**")
    st.markdown("- No cross-org dependencies")
    st.markdown("- Small-medium resource count (<100)")
    st.markdown("- Can migrate in Phase 1")
    st.markdown("- Self-contained workflows")

# Identify most complex orgs
st.markdown("#### 🔍 Most Complex Organizations")

complexity_scores = []
for org_name, report in org_reports.items():
    score = (
        len(report.get("dependencies", {})) * 10
        + report.get("resource_count", 0) / 10
        + (0 if report.get("can_migrate_standalone") else 20)
    )
    complexity_scores.append(
        {
            "org": org_name,
            "score": score,
            "deps": len(report.get("dependencies", {})),
            "resources": report.get("resource_count", 0),
        }
    )

# Sort by complexity
complexity_scores.sort(key=lambda x: x["score"], reverse=True)

# Show top 5
for i, item in enumerate(complexity_scores[:5], 1):
    with st.expander(f"{i}. **{item['org']}** - Complexity Score: {round(item['score'])}"):
        st.markdown(f"**Dependencies:** {item['deps']} organization(s)")
        st.markdown(f"**Resources:** {item['resources']}")
        st.markdown(
            f"**Recommended Action:** {'Migrate in later phase with careful planning' if item['score'] > 50 else 'Standard migration process'}"
        )

st.markdown("---")

# Export dashboard
st.markdown("### 💾 Export Dashboard")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Download Metrics (CSV)", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV", csv, file_name="dashboard_metrics.csv", mime="text/csv"
        )

with col2:
    if st.button("📈 Download Dashboard (PDF)", use_container_width=True):
        st.info("PDF export coming soon!")
