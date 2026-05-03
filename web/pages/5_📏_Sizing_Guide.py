"""Sizing Guide Page - Capacity planning and infrastructure sizing."""

import os
import sys
from pathlib import Path

import requests
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.utils.session import init_session_state

# Initialize session
init_session_state()

# Page config
st.set_page_config(page_title="Sizing Guide", page_icon="📏", layout="wide")

st.title("📏 AAP Capacity Sizing Guide")
st.markdown("Calculate infrastructure requirements for AAP 2.6")
st.markdown("---")

# Get sizing guide URL from environment
SIZING_GUIDE_URL = os.getenv("SIZING_GUIDE_URL", "http://localhost:5002")

# Check if sizing guide is available
try:
    health_response = requests.get(f"{SIZING_GUIDE_URL}/health", timeout=2)
    sizing_guide_available = health_response.status_code == 200
except:
    sizing_guide_available = False

if not sizing_guide_available:
    st.warning("⚠️ Sizing Guide service not available")
    st.info(f"Make sure the sizing guide container is running on {SIZING_GUIDE_URL}")
    st.markdown("""
    **To start the sizing guide:**
    ```bash
    # Using make
    make start

    # Or using podman
    ./podman-start.sh
    ```
    """)
    st.stop()

# Input form
st.markdown("### 📝 Workload Parameters")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Infrastructure")

    managed_hosts = st.number_input(
        "Managed Hosts",
        min_value=1,
        value=1000,
        step=100,
        help="Total number of hosts managed by AAP",
    )

    concurrent_jobs = st.number_input(
        "Concurrent Jobs (Peak)",
        min_value=1,
        value=50,
        step=5,
        help="Maximum concurrent jobs during peak hours",
    )

with col2:
    st.markdown("#### Job Characteristics")

    avg_job_duration = st.number_input(
        "Average Job Duration (minutes)",
        min_value=1,
        value=10,
        step=1,
        help="Average time for a job to complete",
    )

    jobs_per_day = st.number_input(
        "Jobs Per Day", min_value=1, value=500, step=50, help="Total number of jobs executed daily"
    )

    tasks_per_job = st.number_input(
        "Tasks Per Job", min_value=1, value=20, step=5, help="Average number of tasks in each job"
    )

# Advanced settings
with st.expander("⚙️ Advanced Settings"):
    col1, col2 = st.columns(2)

    with col1:
        forks = st.number_input(
            "Forks", min_value=1, value=5, help="Number of parallel processes per job"
        )

        retention_days = st.number_input(
            "Job Retention (days)", min_value=1, value=90, help="How long to keep job history"
        )

    with col2:
        deployment_type = st.selectbox(
            "Deployment Type",
            ["Growth", "Enterprise"],
            help="Growth: Standard HA, Enterprise: Full redundancy",
        )

# Auto-populate from analysis
if st.session_state.analysis_data and st.session_state.analysis_data.get("type") == "global":
    st.info("💡 Tip: We can estimate some values from your analysis data")

    if st.button("📊 Use Analysis Data"):
        # Extract workload info from analysis
        org_reports = st.session_state.analysis_data.get("org_reports", {})
        total_resources = sum(report.get("resource_count", 0) for report in org_reports.values())

        st.success(f"Estimated {total_resources} total resources across all organizations")
        # Could set managed_hosts, jobs estimates, etc.

# Calculate sizing
st.markdown("---")

if st.button("🔬 Calculate Sizing", type="primary", use_container_width=True):
    with st.spinner("Calculating infrastructure requirements..."):
        try:
            # Prepare request
            payload = {
                "managed_hosts": managed_hosts,
                "concurrent_jobs": concurrent_jobs,
                "avg_job_duration_minutes": avg_job_duration,
                "jobs_per_day": jobs_per_day,
                "tasks_per_job": tasks_per_job,
                "forks": forks,
                "retention_days": retention_days,
                "deployment_type": deployment_type.lower(),
            }

            # Call sizing guide API
            response = requests.post(f"{SIZING_GUIDE_URL}/api/calculate", json=payload, timeout=10)

            if response.status_code == 200:
                results = response.json()

                st.success("✅ Sizing calculation complete!")

                # Display results
                st.markdown("### 🖥️ Infrastructure Requirements")

                # Execution Plane
                st.markdown("#### Execution Plane (Task Runner)")
                exec_plane = results.get("execution_plane", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nodes", exec_plane.get("nodes", "N/A"))
                with col2:
                    st.metric("vCPU per Node", exec_plane.get("vcpu_per_node", "N/A"))
                with col3:
                    st.metric("RAM per Node (GB)", exec_plane.get("ram_gb_per_node", "N/A"))
                with col4:
                    st.metric("Total vCPU", exec_plane.get("total_vcpu", "N/A"))

                st.markdown("---")

                # Control Plane
                st.markdown("#### Control Plane (Controllers)")
                control_plane = results.get("control_plane", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nodes", control_plane.get("nodes", "N/A"))
                with col2:
                    st.metric("vCPU per Node", control_plane.get("vcpu_per_node", "N/A"))
                with col3:
                    st.metric("RAM per Node (GB)", control_plane.get("ram_gb_per_node", "N/A"))
                with col4:
                    st.metric("Total vCPU", control_plane.get("total_vcpu", "N/A"))

                st.markdown("---")

                # Database
                st.markdown("#### Database (PostgreSQL)")
                database = results.get("database", {})

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nodes", database.get("nodes", "N/A"))
                with col2:
                    st.metric("vCPU per Node", database.get("vcpu_per_node", "N/A"))
                with col3:
                    st.metric("RAM per Node (GB)", database.get("ram_gb_per_node", "N/A"))

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Storage (GB)", database.get("storage_gb", "N/A"))
                with col2:
                    st.metric("IOPS", database.get("iops", "N/A"))

                st.markdown("---")

                # Summary
                st.markdown("### 📊 Total Requirements")

                summary = results.get("summary", {})

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Total Nodes",
                        summary.get("total_nodes", "N/A"),
                        help="All nodes across execution, control, and database",
                    )
                with col2:
                    st.metric(
                        "Total vCPU",
                        summary.get("total_vcpu", "N/A"),
                        help="Sum of all vCPUs needed",
                    )
                with col3:
                    st.metric(
                        "Total RAM (GB)",
                        summary.get("total_ram_gb", "N/A"),
                        help="Sum of all RAM needed",
                    )

                # Recommendations
                if results.get("recommendations"):
                    st.markdown("### 💡 Recommendations")
                    for rec in results["recommendations"]:
                        st.info(rec)

                # Save results to session
                st.session_state.sizing_results = results

            else:
                st.error(f"❌ Calculation failed: {response.status_code}")
                st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to sizing guide service")
            st.info("Make sure the sizing guide container is running")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Export sizing results
if st.session_state.get("sizing_results"):
    st.markdown("---")
    st.markdown("### 💾 Export Sizing")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Download Results (JSON)", use_container_width=True):
            import json

            json_str = json.dumps(st.session_state.sizing_results, indent=2)
            st.download_button(
                "⬇️ Download", json_str, file_name="aap_sizing.json", mime="application/json"
            )

    with col2:
        if st.button("📊 Download BOM (Bill of Materials)", use_container_width=True):
            st.info("BOM export coming soon!")

# Link to standalone sizing guide
st.markdown("---")
st.markdown("### 🔗 Resources")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Standalone Sizing Calculator:**")
    st.markdown(f"[Open in new tab]({SIZING_GUIDE_URL})")

with col2:
    st.markdown("**Documentation:**")
    st.markdown("[Red Hat AAP Sizing Guide](https://access.redhat.com/documentation)")
