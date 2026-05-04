"""Sizing Guide Page - Capacity planning and infrastructure sizing."""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aap_migration_planner.sizing import AAP26SizingCalculator
from web.utils.session import init_session_state

# Initialize session
init_session_state()

# Page config
st.set_page_config(page_title="Sizing Guide", page_icon="📏", layout="wide")

st.title("📏 AAP Capacity Sizing Guide")
st.markdown("Calculate infrastructure requirements for AAP 2.6 based on AAP 2.4 metrics")
st.markdown("---")

# Initialize calculator
calculator = AAP26SizingCalculator()

# Input form
st.markdown("### 📝 Current AAP 2.4 Metrics")

# Controller metrics
st.markdown("#### Control Plane")
col1, col2 = st.columns(2)

with col1:
    num_controllers = st.number_input(
        "Number of Controllers",
        min_value=1,
        value=3,
        step=1,
        help="Current number of controller nodes in AAP 2.4",
    )

    controller_cpu_avg = st.slider(
        "Controller CPU Usage - Average (%)",
        min_value=0,
        max_value=100,
        value=35,
        help="Average CPU utilization across controllers",
    )

    controller_cpu_peak = st.slider(
        "Controller CPU Usage - Peak (%)",
        min_value=0,
        max_value=100,
        value=50,
        help="Peak CPU utilization during busy periods",
    )

with col2:
    controller_memory = st.slider(
        "Controller Memory Usage (%)",
        min_value=0,
        max_value=100,
        value=20,
        help="Memory utilization on controller nodes",
    )

    num_hub_nodes = st.number_input(
        "Number of Hub Nodes", min_value=0, value=2, step=1, help="Automation Hub nodes"
    )

    hub_cpu = st.slider(
        "Hub CPU Usage (%)", min_value=0, max_value=100, value=25, help="Hub CPU utilization"
    )

# Execution plane metrics
st.markdown("---")
st.markdown("#### Execution Plane")

col1, col2 = st.columns(2)

with col1:
    num_execution = st.number_input(
        "Number of Execution Nodes",
        min_value=1,
        value=10,
        step=1,
        help="Current execution nodes",
    )

    execution_cpu = st.slider(
        "Execution Node CPU Usage (%)",
        min_value=0,
        max_value=100,
        value=70,
        help="Average CPU on execution nodes",
    )

with col2:
    execution_memory = st.slider(
        "Execution Node Memory Usage (%)",
        min_value=0,
        max_value=100,
        value=50,
        help="Memory utilization on execution nodes",
    )

    forks_observed = st.number_input(
        "Observed Forks", min_value=1, value=5, help="Typical fork count in jobs"
    )

# Database metrics
st.markdown("---")
st.markdown("#### Database")

col1, col2 = st.columns(2)

with col1:
    db_vcpu = st.number_input(
        "Database vCPU", min_value=1, value=8, step=1, help="Database vCPU allocation"
    )

    db_memory_gb = st.number_input(
        "Database Memory (GB)", min_value=1, value=64, step=8, help="Database RAM in GB"
    )

    db_cpu_percent = st.slider(
        "Database CPU Usage (%)",
        min_value=0,
        max_value=100,
        value=60,
        help="Database CPU utilization",
    )

with col2:
    db_memory_percent = st.slider(
        "Database Memory Usage (%)",
        min_value=0,
        max_value=100,
        value=35,
        help="Database memory utilization",
    )

    db_requests_peak = st.number_input(
        "Concurrent DB Requests (Peak)",
        min_value=1,
        value=300,
        help="Peak concurrent database connections",
    )

    db_growth_gb = st.number_input(
        "DB Growth Per Day (GB)", min_value=0, value=50, help="Daily database growth"
    )

# Workload metrics
st.markdown("---")
st.markdown("#### Workload Characteristics")

col1, col2 = st.columns(2)

with col1:
    playbooks_per_day = st.number_input(
        "Playbooks Per Day (Peak)",
        min_value=1,
        value=10000,
        step=1000,
        help="Peak daily job executions",
    )

    concurrent_jobs = st.number_input(
        "Concurrent Jobs (Peak)",
        min_value=1,
        value=100,
        step=10,
        help="Maximum concurrent jobs",
    )

    concurrent_pending = st.number_input(
        "Concurrent Jobs Pending", min_value=0, value=20, help="Jobs waiting in queue"
    )

with col2:
    managed_hosts = st.number_input(
        "Managed Hosts",
        min_value=1,
        value=5000,
        step=100,
        help="Total hosts under management",
    )

    tasks_per_job = st.number_input(
        "Tasks Per Job (Avg)", min_value=1, value=50, help="Average tasks per playbook"
    )

    job_duration_hours = st.number_input(
        "Job Duration (Hours)",
        min_value=0.1,
        max_value=24.0,
        value=0.25,
        step=0.25,
        help="Average job execution time",
    )

# Advanced settings
with st.expander("⚙️ Advanced Settings"):
    col1, col2 = st.columns(2)

    with col1:
        retention_hours = st.number_input(
            "Job Retention (Hours)", min_value=1, value=48, help="How long to keep job history"
        )

        allowed_hours = st.number_input(
            "Allowed Hours Per Day",
            min_value=1,
            max_value=24,
            value=24,
            help="Hours available for job execution",
        )

        verbosity = st.selectbox(
            "Verbosity Level",
            options=[0, 1, 2, 3, 4],
            index=1,
            format_func=lambda x: {
                0: "Minimal (0)",
                1: "Normal (1) - Recommended",
                2: "Verbose (2)",
                3: "Debug (3)",
                4: "Connection Debug (4)",
            }[x],
            help="Ansible verbosity level affects event processing load",
        )

    with col2:
        peak_pattern = st.selectbox(
            "Peak Concurrency Pattern",
            options=["distributed_24x7", "business_hours", "batch_window", "mixed"],
            index=0,
            format_func=lambda x: {
                "distributed_24x7": "Distributed 24/7 (1.0x)",
                "business_hours": "Business Hours (2.5x)",
                "batch_window": "Batch Window (10.0x)",
                "mixed": "Mixed Pattern (1.5x)",
            }[x],
            help="How jobs are distributed throughout the day",
        )

        hub_memory = st.slider(
            "Hub Memory Usage (%)", min_value=0, max_value=100, value=30, help="Hub memory %"
        )

# Auto-populate from analysis
if st.session_state.analysis_data and st.session_state.analysis_data.get("type") == "global":
    st.info("💡 Tip: We can estimate some values from your analysis data")

    if st.button("📊 Auto-Fill from Analysis"):
        # Extract workload info from analysis
        org_reports = st.session_state.analysis_data.get("org_reports", {})

        # Count resources to estimate workload
        total_job_templates = 0
        total_projects = 0
        total_inventories = 0

        for report in org_reports.values():
            resources = report.get("resources", {})
            total_job_templates += len(resources.get("job_templates", []))
            total_projects += len(resources.get("projects", []))
            total_inventories += len(resources.get("inventories", []))

        st.success(
            f"Found: {total_job_templates} job templates, "
            f"{total_projects} projects, {total_inventories} inventories"
        )

        # Could update managed_hosts based on inventories, etc.
        st.rerun()

# Calculate sizing
st.markdown("---")

if st.button("🔬 Calculate AAP 2.6 Sizing", type="primary", use_container_width=True):
    with st.spinner("Calculating infrastructure requirements..."):
        try:
            # Prepare metrics dictionary
            metrics = {
                "num_controllers": num_controllers,
                "controller_cpu_percent_avg": controller_cpu_avg,
                "controller_cpu_percent_peak": controller_cpu_peak,
                "controller_memory_percent": controller_memory,
                "num_hub_nodes": num_hub_nodes,
                "hub_cpu_percent": hub_cpu,
                "hub_memory_percent": hub_memory,
                "num_execution_nodes": num_execution,
                "execution_cpu_percent": execution_cpu,
                "execution_memory_percent": execution_memory,
                "forks_observed": forks_observed,
                "database_vcpu": db_vcpu,
                "database_memory_gb": db_memory_gb,
                "database_cpu_percent": db_cpu_percent,
                "database_memory_percent": db_memory_percent,
                "concurrent_db_requests_peak": db_requests_peak,
                "db_growth_per_day_gb": db_growth_gb,
                "playbooks_per_day_peak": playbooks_per_day,
                "concurrent_jobs_peak": concurrent_jobs,
                "concurrent_jobs_pending": concurrent_pending,
                "job_retention_hours": retention_hours,
                "managed_hosts": managed_hosts,
                "tasks_per_job": tasks_per_job,
                "job_duration_hours": job_duration_hours,
                "allowed_hours_per_day": allowed_hours,
                "verbosity_level": verbosity,
                "peak_pattern": peak_pattern,
            }

            # Calculate sizing
            results = calculator.generate_sizing_recommendation(metrics)

            st.success("✅ Sizing calculation complete!")

            # Display warnings if any
            if results.get("warnings"):
                st.warning("⚠️ **Warnings:**")
                for warning in results["warnings"]:
                    st.warning(f"- {warning}")

            # Display results
            st.markdown("### 🖥️ AAP 2.6 Infrastructure Requirements")

            # Gateway
            st.markdown("#### Gateway (API/UI)")
            gateway = results.get("gateway", {})

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nodes", gateway.get("nodes", "N/A"))
            with col2:
                st.metric("CPU per Node", f"{gateway.get('cpu_per_node', 'N/A')}")
            with col3:
                st.metric("Memory per Node (GB)", f"{gateway.get('memory_per_node_gb', 'N/A')}")
            with col4:
                st.metric("Total CPU", f"{gateway.get('total_cpu', 'N/A')}")

            st.markdown("---")

            # Controller (Event Driven)
            st.markdown("#### Controller (Event Processing)")
            controller = results.get("controller", {})

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nodes", controller.get("nodes", "N/A"))
            with col2:
                st.metric("CPU per Node", f"{controller.get('cpu_per_node', 'N/A')}")
            with col3:
                st.metric("Memory per Node (GB)", f"{controller.get('memory_per_node_gb', 'N/A')}")
            with col4:
                st.metric("Total CPU", f"{controller.get('total_cpu', 'N/A')}")

            st.markdown("---")

            # Execution Plane
            st.markdown("#### Execution Plane (Task Runner)")
            execution = results.get("execution", {})

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nodes", execution.get("nodes", "N/A"))
            with col2:
                st.metric("CPU per Node", f"{execution.get('cpu_per_node', 'N/A')}")
            with col3:
                st.metric("Memory per Node (GB)", f"{execution.get('memory_per_node_gb', 'N/A')}")
            with col4:
                st.metric("Total CPU", f"{execution.get('total_cpu', 'N/A')}")

            st.markdown("---")

            # Database
            st.markdown("#### Database (PostgreSQL)")
            database = results.get("database", {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("CPU", f"{database.get('cpu', 'N/A')}")
            with col2:
                st.metric("Memory (GB)", f"{database.get('memory_gb', 'N/A')}")
            with col3:
                st.metric("Storage (GB)", f"{database.get('storage_gb', 'N/A')}")

            st.markdown("---")

            # Automation Hub
            st.markdown("#### Automation Hub")
            hub = results.get("hub", {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nodes", hub.get("nodes", "N/A"))
            with col2:
                st.metric("CPU per Node", f"{hub.get('cpu_per_node', 'N/A')}")
            with col3:
                st.metric("Memory per Node (GB)", f"{hub.get('memory_per_node_gb', 'N/A')}")

            st.markdown("---")

            # Summary
            st.markdown("### 📊 Total Requirements")

            total_nodes = (
                gateway.get("nodes", 0)
                + controller.get("nodes", 0)
                + execution.get("nodes", 0)
                + hub.get("nodes", 0)
            )
            total_cpu = results.get("total_cpu", 0)
            total_memory = results.get("total_memory_gb", 0)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Nodes", total_nodes, help="All container nodes")
            with col2:
                st.metric("Total CPU", f"{total_cpu:.1f}", help="Sum of all CPU cores")
            with col3:
                st.metric("Total Memory (GB)", f"{total_memory:.1f}", help="Sum of all RAM")

            # Save results to session
            st.session_state.sizing_results = results

        except Exception as e:
            st.error(f"❌ Error calculating sizing: {str(e)}")
            import traceback

            with st.expander("Show error details"):
                st.code(traceback.format_exc())

# Export sizing results
if st.session_state.get("sizing_results"):
    st.markdown("---")
    st.markdown("### 💾 Export Sizing")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Download Results (JSON)", use_container_width=True):
            import json

            json_str = json.dumps(st.session_state.sizing_results, indent=2, default=str)
            st.download_button(
                "⬇️ Download", json_str, file_name="aap26_sizing.json", mime="application/json"
            )

    with col2:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Sizing report generation coming soon!")

# Documentation
st.markdown("---")
st.markdown("### 📚 Resources")

st.markdown("""
**Using Official Red Hat Formulas:**
- Based on Red Hat's AAP 2.4 to 2.6 migration sizing guide
- Includes event processing overhead calculations
- Accounts for verbosity levels and peak patterns
- Validates against recommended minimums

**Need Help?**
- [Red Hat AAP Documentation](https://access.redhat.com/documentation/en-us/red_hat_ansible_automation_platform/)
- [AAP Sizing Guide](https://access.redhat.com/articles/AAP_sizing)
""")
