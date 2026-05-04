"""Migration Plan Page - Phase-by-phase migration timeline."""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.components.phase_timeline import render_migration_timeline
from web.utils.session import init_session_state, is_connected

# Initialize session
init_session_state()

# Page config
st.set_page_config(page_title="Migration Plan", page_icon="📋", layout="wide")

st.title("📋 Migration Plan")
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
    st.warning("⚠️ Migration plan is only available for global (all organizations) analysis.")
    st.info("👉 Go to **Analysis** page and run analysis with 'All Organizations' mode")
    st.stop()

# Migration summary
st.markdown("### 📊 Migration Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Phases", len(data.get("migration_phases", [])))

with col2:
    st.metric("Total Organizations", data.get("total_organizations", 0))

with col3:
    # Calculate estimated duration (placeholder)
    phases = len(data.get("migration_phases", []))
    estimated_days = phases * 7  # Assume 1 week per phase
    st.metric(
        "Estimated Duration",
        f"{estimated_days} days",
        help="Estimated timeline assuming 1 week per phase",
    )

st.markdown("---")

# Migration order
st.markdown("### 🗓️ Migration Order")

migration_order = data.get("migration_order", [])
if migration_order:
    # Display as numbered list
    order_text = ""
    for idx, org in enumerate(migration_order, 1):
        order_text += f"{idx}. **{org}**\n\n"

    st.markdown(order_text)
else:
    st.info("No migration order calculated")

st.markdown("---")

# Phase details
st.markdown("### 📅 Migration Phases")

migration_phases = data.get("migration_phases", [])
if migration_phases:
    # Render timeline visualization
    render_migration_timeline(migration_phases, data.get("org_reports", {}))

    # Phase breakdown
    for phase in migration_phases:
        phase_num = phase.get("phase")
        orgs = phase.get("orgs", [])
        description = phase.get("description", "")

        with st.expander(
            f"**Phase {phase_num}** - {len(orgs)} organization(s)", expanded=(phase_num == 1)
        ):
            st.markdown(f"**Description:** {description}")
            st.markdown(f"**Organizations:** {', '.join(orgs)}")

            # Show resource counts
            org_reports = data.get("org_reports", {})
            total_resources = sum(org_reports.get(org, {}).get("resource_count", 0) for org in orgs)
            st.markdown(f"**Total Resources:** {total_resources}")

            # Can migrate in parallel
            if len(orgs) > 1:
                st.success(f"✅ These {len(orgs)} organizations can migrate in parallel")
            else:
                st.info("ℹ️ Single organization in this phase")

            # Dependencies satisfied
            st.markdown("**Dependencies:**")
            all_independent = True
            for org in orgs:
                org_data = org_reports.get(org, {})
                deps = org_data.get("required_migrations_before", [])
                if deps:
                    all_independent = False
                    st.markdown(f"  - **{org}** requires: {', '.join(deps)}")
                else:
                    st.markdown(f"  - **{org}**: No dependencies")

            if all_independent and phase_num > 1:
                st.warning(
                    "⚠️ Note: While these orgs have no internal dependencies, they should migrate after Phase 1"
                )

else:
    st.info("No migration phases calculated")

st.markdown("---")

# Recommendations
st.markdown("### 💡 Recommendations")

independent_orgs = data.get("independent_orgs", [])
dependent_orgs = data.get("dependent_orgs", [])

if independent_orgs:
    st.success(
        f"✅ **Independent Organizations ({len(independent_orgs)})**: {', '.join(independent_orgs)}"
    )
    st.markdown("These can be migrated first or independently without risk.")

if dependent_orgs:
    st.warning(
        f"⚠️ **Dependent Organizations ({len(dependent_orgs)})**: {', '.join(dependent_orgs)}"
    )
    st.markdown("These have cross-org dependencies and must follow the migration order.")

# Risk assessment
st.markdown("### ⚠️ Risk Assessment")

# Calculate risks
org_reports = data.get("org_reports", {})
high_risk_orgs = []
medium_risk_orgs = []
low_risk_orgs = []

for org_name, report in org_reports.items():
    dep_count = len(report.get("dependencies", {}))
    resource_count = report.get("resource_count", 0)

    # Simple risk scoring
    if dep_count >= 3 or resource_count > 200:
        high_risk_orgs.append(org_name)
    elif dep_count >= 1 or resource_count > 100:
        medium_risk_orgs.append(org_name)
    else:
        low_risk_orgs.append(org_name)

col1, col2, col3 = st.columns(3)

with col1:
    if high_risk_orgs:
        st.error(f"**High Risk ({len(high_risk_orgs)})**")
        for org in high_risk_orgs:
            st.markdown(f"  - {org}")
    else:
        st.success("**High Risk (0)**")

with col2:
    if medium_risk_orgs:
        st.warning(f"**Medium Risk ({len(medium_risk_orgs)})**")
        for org in medium_risk_orgs:
            st.markdown(f"  - {org}")
    else:
        st.info("**Medium Risk (0)**")

with col3:
    if low_risk_orgs:
        st.success(f"**Low Risk ({len(low_risk_orgs)})**")
        for org in low_risk_orgs:
            st.markdown(f"  - {org}")
    else:
        st.info("**Low Risk (0)**")

st.markdown("---")

# Export migration plan
st.markdown("### 💾 Export Migration Plan")

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Download Plan (JSON)", use_container_width=True):
        import json

        plan_data = {
            "migration_order": migration_order,
            "migration_phases": migration_phases,
            "independent_orgs": independent_orgs,
            "dependent_orgs": dependent_orgs,
            "total_organizations": data.get("total_organizations"),
        }
        json_str = json.dumps(plan_data, indent=2)
        st.download_button(
            "⬇️ Download", json_str, file_name="migration_plan.json", mime="application/json"
        )

with col2:
    if st.button("📊 Download Plan (PDF)", use_container_width=True):
        st.info("PDF export coming soon!")
