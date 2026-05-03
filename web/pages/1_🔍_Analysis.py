"""Dependency Analysis Page - Interactive dependency graph visualization."""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aap_migration_planner.database import DatabaseService
from web.components.graph import render_dependency_graph
from web.utils.data_loader import get_sample_data, save_to_file
from web.utils.session import get_connection_config, init_session_state, is_connected

# Initialize session
init_session_state()

# Page config
st.set_page_config(page_title="Dependency Analysis", page_icon="🔍", layout="wide")

st.title("🔍 Dependency Analysis")
st.markdown("---")

# Check connection
if not is_connected():
    st.warning("⚠️ Not connected to AAP. Please connect in the main page.")
    st.stop()

# Cache Statistics
try:
    db_service = DatabaseService(db_path="data/aap_analysis.db")
    stats = db_service.get_stats()

    if stats["total_orgs"] > 0:
        with st.expander("📊 Cache Statistics", expanded=False):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Cached Organizations", stats["total_orgs"])

            with col2:
                st.metric("Cached Resources", f"{stats['total_resources']:,}")

            with col3:
                st.metric("Dependencies Tracked", stats["total_dependencies"])

            with col4:
                if stats["last_analysis"]:
                    st.metric("Last Analysis", stats["last_analysis"].strftime("%Y-%m-%d %H:%M"))
                else:
                    st.metric("Last Analysis", "Never")

            col_a, col_b = st.columns([3, 1])

            with col_a:
                st.caption(
                    "✅ Using database cache for faster analysis. Fresh data fetched only for changed orgs."
                )

            with col_b:
                if st.button("🗑️ Clear Cache", use_container_width=True):
                    # Clear all orgs
                    for org in db_service.get_all_organizations():
                        db_service.clear_organization(org.name)
                    st.success("Cache cleared!")
                    st.rerun()
except Exception:
    pass  # Database not initialized yet

# Analysis controls
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    analysis_mode = st.radio(
        "Analysis Mode", ["All Organizations", "Specific Organization"], horizontal=True
    )

with col2:
    if analysis_mode == "Specific Organization":
        org_name = st.text_input("Organization Name", placeholder="Engineering")
    else:
        org_name = None

with col3:
    use_sample = st.checkbox("Use Sample Data", help="Use demo data instead of live AAP")

# Advanced settings
with st.expander("⚙️ Advanced Settings"):
    st.markdown("**Parallelism Configuration**")
    col1, col2 = st.columns(2)

    with col1:
        max_concurrent_orgs = st.slider(
            "Max Concurrent Organizations",
            min_value=1,
            max_value=20,
            value=5,
            help="How many organizations to analyze in parallel. Higher = faster but more load on AAP.",
        )

    with col2:
        max_concurrent_resources = st.slider(
            "Max Concurrent Resource Fetches",
            min_value=5,
            max_value=50,
            value=20,
            help="How many resource types to fetch in parallel per org. Higher = faster but more API calls.",
        )

    st.caption(
        f"⚡ Estimated speedup: {max_concurrent_orgs}x for orgs, {max_concurrent_resources}x for resources"
    )
    st.caption(
        "⚠️ Note: Higher values may hit AAP rate limits. Start with defaults and increase if needed."
    )

# Run analysis button
if st.button("🔍 Run Analysis", type="primary", use_container_width=True):
    if use_sample:
        st.session_state.analysis_data = get_sample_data()
        st.success("✅ Sample data loaded!")
    else:
        # Progress tracking UI
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            eta_text = st.empty()

        import asyncio
        import time

        from web.utils.data_loader import run_analysis_async

        start_time = time.time()
        progress_data = {"current": 0, "total": 1, "message": "Starting..."}

        def update_progress(current, total, message):
            """Progress callback to update UI."""
            progress_data["current"] = current
            progress_data["total"] = total
            progress_data["message"] = message

            # Update progress bar
            if total > 0:
                progress = current / total
                progress_bar.progress(progress)

                # Calculate ETA
                elapsed = time.time() - start_time
                if current > 0:
                    rate = elapsed / current
                    remaining = (total - current) * rate
                    eta_min = int(remaining / 60)
                    eta_sec = int(remaining % 60)
                    eta_text.caption(
                        f"⏱️ ETA: {eta_min}m {eta_sec}s | Speed: {current/elapsed:.1f} orgs/sec"
                    )

            # Update status
            status_text.info(f"📊 {message} ({current}/{total})")

        # Run async analysis with progress tracking
        config = get_connection_config()

        try:
            result = asyncio.run(
                run_analysis_async(
                    config["url"],
                    config["token"],
                    config["verify_ssl"],
                    org_name,
                    progress_callback=update_progress,
                    max_concurrent_orgs=max_concurrent_orgs,
                    max_concurrent_resources=max_concurrent_resources,
                )
            )

            if result:
                progress_bar.progress(1.0)
                status_text.success("✅ Analysis complete!")

                elapsed_total = time.time() - start_time
                total_orgs = progress_data.get("total", 0)
                eta_text.success(
                    f"✅ Completed in {int(elapsed_total/60)}m {int(elapsed_total%60)}s | Analyzed {total_orgs} organizations"
                )

                st.session_state.analysis_data = result
                st.success("✅ Analysis complete!")

                # Save to file
                save_to_file(result, "data/latest_analysis.json")
            else:
                st.error("❌ Analysis failed")

        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            import traceback

            with st.expander("Show error details"):
                st.code(traceback.format_exc())

# Display results
if st.session_state.analysis_data:
    data = st.session_state.analysis_data

    # Summary metrics
    st.markdown("### 📊 Summary")

    if data.get("type") == "global":
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Organizations", data.get("total_organizations", 0))

        with col2:
            st.metric(
                "Independent",
                len(data.get("independent_orgs", [])),
                help="Organizations with no dependencies",
            )

        with col3:
            st.metric(
                "Dependent",
                len(data.get("dependent_orgs", [])),
                help="Organizations with cross-org dependencies",
            )

        with col4:
            total_deps = sum(
                len(report.get("dependencies", {}))
                for report in data.get("org_reports", {}).values()
            )
            st.metric("Dependencies", total_deps, help="Total cross-org dependency relationships")

    st.markdown("---")

    # Dependency Graph
    st.markdown("### 🕸️ Dependency Graph")

    if data.get("type") == "global":
        # Build graph data
        render_dependency_graph(data)
    else:
        st.info("Dependency graph available for global analysis only")

    st.markdown("---")

    # Organization Details
    st.markdown("### 📋 Organization Details")

    if data.get("type") == "global":
        org_reports = data.get("org_reports", {})

        # Filter options
        filter_option = st.radio(
            "Show", ["All", "Independent Only", "Dependent Only"], horizontal=True
        )

        for org_name, report in org_reports.items():
            has_deps = report.get("has_cross_org_deps", False)

            # Apply filter
            if filter_option == "Independent Only" and has_deps:
                continue
            if filter_option == "Dependent Only" and not has_deps:
                continue

            with st.expander(f"**{org_name}** - {report.get('resource_count', 0)} resources"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Organization ID:** {report.get('org_id')}")
                    st.markdown(f"**Total Resources:** {report.get('resource_count', 0)}")
                    st.markdown(
                        f"**Can Migrate Standalone:** {'✅ Yes' if report.get('can_migrate_standalone') else '❌ No'}"
                    )

                with col2:
                    deps = report.get("dependencies", {})
                    if deps:
                        st.markdown(f"**Dependencies ({len(deps)} org(s)):**")
                        for dep_org, dep_resources in deps.items():
                            st.markdown(f"  - {dep_org}: {len(dep_resources)} resource(s)")
                    else:
                        st.markdown("**Dependencies:** None")

                # Show required migrations before
                req_before = report.get("required_migrations_before", [])
                if req_before:
                    st.info(f"⚠️ Must migrate these organizations first: {', '.join(req_before)}")

                # Detailed dependency breakdown
                deps = report.get("dependencies", {})
                if deps:
                    st.markdown("---")
                    st.markdown("#### 🔍 Detailed Dependencies")

                    for dep_org, dep_resources in deps.items():
                        with st.expander(
                            f"📦 Dependencies on **{dep_org}** ({len(dep_resources)} resources)"
                        ):
                            # Group by resource type
                            by_type = {}
                            for dep in dep_resources:
                                res_type = dep.get("resource_type", "unknown")
                                if res_type not in by_type:
                                    by_type[res_type] = []
                                by_type[res_type].append(dep)

                            for res_type, resources in sorted(by_type.items()):
                                st.markdown(
                                    f"**{res_type.replace('_', ' ').title()}** ({len(resources)})"
                                )

                                # Create table data
                                import pandas as pd

                                table_data = []
                                for dep in resources:
                                    required_by = dep.get("required_by", [])
                                    required_by_str = ", ".join(
                                        [
                                            f"{r.get('name', 'unknown')} ({r.get('type', 'unknown')})"
                                            for r in required_by[:3]
                                        ]
                                    )
                                    if len(required_by) > 3:
                                        required_by_str += f" ... +{len(required_by) - 3} more"

                                    table_data.append(
                                        {
                                            "Resource Name": dep.get("resource_name", "N/A"),
                                            "ID": dep.get("resource_id", "N/A"),
                                            "Used By": required_by_str
                                            if required_by_str
                                            else "N/A",
                                        }
                                    )

                                if table_data:
                                    df = pd.DataFrame(table_data)
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                                st.markdown("")

                # Resource Inventory - All resources in this organization
                resources = report.get("resources", {})
                if resources:
                    st.markdown("---")
                    st.markdown("#### 📦 Resource Inventory")
                    st.caption("All resources in this organization")

                    # Summary by type
                    resource_counts = {
                        rtype: len(items) for rtype, items in resources.items() if items
                    }
                    if resource_counts:
                        cols = st.columns(min(4, len(resource_counts)))
                        for idx, (rtype, count) in enumerate(sorted(resource_counts.items())):
                            with cols[idx % len(cols)]:
                                st.metric(rtype.replace("_", " ").title(), count)

                    # Detailed resource tables
                    for rtype, items in sorted(resources.items()):
                        if not items:
                            continue

                        with st.expander(f"📋 {rtype.replace('_', ' ').title()} ({len(items)})"):
                            import pandas as pd

                            table_data = []
                            for item in items:
                                table_data.append(
                                    {
                                        "Name": item.get("name", "N/A"),
                                        "ID": item.get("id", "N/A"),
                                        "Description": item.get("description", "")[:100]
                                        + ("..." if len(item.get("description", "")) > 100 else ""),
                                    }
                                )

                            if table_data:
                                df = pd.DataFrame(table_data)
                                st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        # Single org report
        report = data.get("report", {})
        st.markdown(f"**Organization:** {report.get('org_name')}")
        st.markdown(f"**Total Resources:** {report.get('resource_count', 0)}")
        st.markdown(
            f"**Can Migrate Standalone:** {'✅ Yes' if report.get('can_migrate_standalone') else '❌ No'}"
        )

        deps = report.get("dependencies", {})
        if deps:
            st.markdown(f"**Dependencies ({len(deps)} org(s)):**")
            for dep_org, dep_resources in deps.items():
                st.markdown(f"  - **{dep_org}**: {len(dep_resources)} resource(s)")

            # Detailed dependency breakdown
            st.markdown("---")
            st.markdown("### 🔍 Detailed Dependencies")

            for dep_org, dep_resources in deps.items():
                st.markdown(f"#### 📦 Dependencies on **{dep_org}**")

                # Group by resource type
                by_type = {}
                for dep in dep_resources:
                    res_type = dep.get("resource_type", "unknown")
                    if res_type not in by_type:
                        by_type[res_type] = []
                    by_type[res_type].append(dep)

                for res_type, resources in sorted(by_type.items()):
                    with st.expander(
                        f"**{res_type.replace('_', ' ').title()}** ({len(resources)})"
                    ):
                        # Create table data
                        import pandas as pd

                        table_data = []
                        for dep in resources:
                            required_by = dep.get("required_by", [])
                            required_by_str = ", ".join(
                                [
                                    f"{r.get('name', 'unknown')} ({r.get('type', 'unknown')})"
                                    for r in required_by[:3]
                                ]
                            )
                            if len(required_by) > 3:
                                required_by_str += f" ... +{len(required_by) - 3} more"

                            table_data.append(
                                {
                                    "Resource Name": dep.get("resource_name", "N/A"),
                                    "ID": dep.get("resource_id", "N/A"),
                                    "Used By": required_by_str if required_by_str else "N/A",
                                }
                            )

                        if table_data:
                            df = pd.DataFrame(table_data)
                            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No dependencies - can migrate independently!")

    # Export options
    st.markdown("---")
    st.markdown("### 💾 Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Download JSON", use_container_width=True):
            import json

            json_str = json.dumps(data, indent=2, default=str)
            st.download_button(
                "⬇️ Download", json_str, file_name="analysis.json", mime="application/json"
            )

    with col2:
        if st.button("🖼️ Download Graph", use_container_width=True):
            st.info("Graph export coming soon!")

    with col3:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation coming soon!")

else:
    st.info("👆 Click 'Run Analysis' to get started")
