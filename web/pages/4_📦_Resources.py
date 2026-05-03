"""Resource Browser - View all resources across organizations and global scope."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Resources", page_icon="📦", layout="wide")

st.title("📦 Resource Browser")
st.markdown("Browse all resources in AAP including organization-scoped and global resources")

# Check if analysis data exists
if "analysis_data" not in st.session_state or not st.session_state.analysis_data:
    st.warning(
        "⚠️ No analysis data available. Please run an analysis first from the 🔍 Analysis page."
    )
    st.stop()

data = st.session_state.analysis_data

if data.get("type") != "global":
    st.info("📊 Full resource browser is available for global analysis only.")
    st.stop()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 By Organization", "🌐 Global Resources", "🔍 Search"])

with tab1:
    st.markdown("### 📋 Resources by Organization")

    org_reports = data.get("org_reports", {})

    # Organization selector
    org_names = sorted(org_reports.keys())
    selected_org = st.selectbox("Select Organization", org_names, key="org_selector")

    if selected_org:
        report = org_reports[selected_org]
        resources = report.get("resources", {})

        # Summary metrics
        st.markdown(f"#### {selected_org}")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Organization ID", report.get("org_id"))
        with col2:
            total_resources = sum(len(items) for items in resources.values() if items)
            st.metric("Total Resources", total_resources)
        with col3:
            resource_types = len([rt for rt, items in resources.items() if items])
            st.metric("Resource Types", resource_types)

        st.markdown("---")

        # Resource type selector
        available_types = sorted([rt for rt, items in resources.items() if items])

        if not available_types:
            st.info("No resources found in this organization")
        else:
            selected_type = st.selectbox(
                "Select Resource Type",
                available_types,
                format_func=lambda x: f"{x.replace('_', ' ').title()} ({len(resources.get(x, []))})",
                key="type_selector",
            )

            if selected_type:
                items = resources.get(selected_type, [])

                st.markdown(f"#### {selected_type.replace('_', ' ').title()}")
                st.caption(f"{len(items)} resources")

                # Build dataframe with common fields
                table_data = []
                for item in items:
                    row = {
                        "ID": item.get("id", "N/A"),
                        "Name": item.get("name", "N/A"),
                    }

                    # Add type-specific fields
                    if selected_type == "projects":
                        row["SCM Type"] = item.get("scm_type", "N/A")
                        row["SCM URL"] = item.get("scm_url", "N/A")[:50]
                    elif selected_type == "inventories":
                        row["Kind"] = item.get("kind", "N/A")
                        row["Total Hosts"] = item.get("total_hosts", 0)
                    elif selected_type == "job_templates":
                        row["Project"] = (
                            item.get("summary_fields", {}).get("project", {}).get("name", "N/A")
                        )
                        row["Inventory"] = (
                            item.get("summary_fields", {}).get("inventory", {}).get("name", "N/A")
                        )
                    elif selected_type == "credentials":
                        row["Type"] = (
                            item.get("summary_fields", {})
                            .get("credential_type", {})
                            .get("name", "N/A")
                        )
                    elif selected_type == "workflow_job_templates":
                        row["Nodes"] = (
                            item.get("summary_fields", {})
                            .get("workflow_job_template_nodes", {})
                            .get("count", 0)
                        )

                    row["Description"] = (
                        (item.get("description", "")[:80] + "...")
                        if len(item.get("description", "")) > 80
                        else item.get("description", "")
                    )
                    row["Modified"] = item.get("modified", "N/A")[:19]

                    table_data.append(row)

                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Show detailed view for selected resource
                    st.markdown("---")
                    with st.expander("🔍 View Resource Details"):
                        resource_ids = [item.get("id") for item in items]
                        selected_id = st.selectbox("Select Resource ID", resource_ids)

                        if selected_id:
                            selected_item = next(
                                (item for item in items if item.get("id") == selected_id), None
                            )
                            if selected_item:
                                st.json(selected_item)

with tab2:
    st.markdown("### 🌐 Global Resources")
    st.caption("Resources not tied to any specific organization")

    global_resources = data.get("global_resources", {})

    if not global_resources or all(not items for items in global_resources.values()):
        st.info("""
        **Note:** No global resources found or data not available.

        Global resources in AAP typically include:
        - 🔧 Credential Types (custom types available to all orgs)
        - 🐳 Execution Environments (container images)
        - 🖥️ Instance Groups (controller nodes)
        - 📊 System-level Notification Templates

        These are system-level resources shared across all organizations.
        Re-run the analysis to fetch global resource data.
        """)
    else:
        # Summary metrics
        total_global = sum(len(items) for items in global_resources.values() if items)
        resource_types_count = len([rt for rt, items in global_resources.items() if items])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Global Resources", total_global)
        with col2:
            st.metric("Resource Types", resource_types_count)

        st.markdown("---")

        # Display each resource type
        for rtype, items in sorted(global_resources.items()):
            if not items:
                continue

            with st.expander(f"🔧 {rtype.replace('_', ' ').title()} ({len(items)})", expanded=True):
                table_data = []
                for item in items:
                    row = {
                        "ID": item.get("id", "N/A"),
                        "Name": item.get("name", "N/A"),
                    }

                    # Type-specific fields
                    if rtype == "credential_types":
                        row["Kind"] = item.get("kind", "N/A")
                        row["Managed"] = "✅ Yes" if item.get("managed") else "❌ No"
                    elif rtype == "execution_environments":
                        row["Image"] = item.get("image", "N/A")
                    elif rtype == "instance_groups":
                        row["Instances"] = item.get("instances", 0)
                        row["Policy"] = item.get("policy_instance_percentage", "N/A")
                    elif rtype == "notification_templates":
                        row["Type"] = item.get("notification_type", "N/A")

                    row["Description"] = (
                        (item.get("description", "")[:80] + "...")
                        if len(item.get("description", "")) > 80
                        else item.get("description", "")
                    )

                    table_data.append(row)

                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # JSON viewer
                    if st.checkbox(f"Show JSON data for {rtype}", key=f"json_{rtype}"):
                        st.json(items)

with tab3:
    st.markdown("### 🔍 Search All Resources")

    search_query = st.text_input(
        "🔍 Search by name or description", placeholder="Enter search term..."
    )

    if search_query:
        search_results = []
        org_reports = data.get("org_reports", {})

        for org_name, report in org_reports.items():
            resources = report.get("resources", {})
            for rtype, items in resources.items():
                for item in items:
                    name = item.get("name", "").lower()
                    desc = item.get("description", "").lower()

                    if search_query.lower() in name or search_query.lower() in desc:
                        search_results.append(
                            {
                                "Organization": org_name,
                                "Type": rtype.replace("_", " ").title(),
                                "ID": item.get("id"),
                                "Name": item.get("name"),
                                "Description": (item.get("description", "")[:100] + "...")
                                if len(item.get("description", "")) > 100
                                else item.get("description", ""),
                            }
                        )

        if search_results:
            st.success(f"Found {len(search_results)} matching resources")
            df = pd.DataFrame(search_results)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No resources found matching your search")

st.markdown("---")
st.caption("💡 Tip: Use the Analysis page to view cross-org dependencies")
