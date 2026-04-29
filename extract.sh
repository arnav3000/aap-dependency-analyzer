#!/bin/bash
# Extraction script - Copy and refactor code from aap-bridge-fork

set -e

SRC_REPO="/Users/arbhati/project/git/aap-bridge-fork"
DEST_REPO="/Users/arbhati/project/git/aap-migration-planner"

echo "Starting code extraction from aap-bridge-fork..."

# Copy analysis files
echo "Copying analysis module..."
cp "$SRC_REPO/src/aap_migration/analysis/dependency_analyzer.py" \
   "$DEST_REPO/src/aap_migration_planner/analysis/analyzer.py"

cp "$SRC_REPO/src/aap_migration/analysis/dependency_graph.py" \
   "$DEST_REPO/src/aap_migration_planner/analysis/graph.py"

# Copy reporting files
echo "Copying reporting module..."
cp "$SRC_REPO/src/aap_migration/analysis/html_report.py" \
   "$DEST_REPO/src/aap_migration_planner/reporting/html_report.py"

cp "$SRC_REPO/src/aap_migration/analysis/reports.py" \
   "$DEST_REPO/src/aap_migration_planner/reporting/text_report.py"

# Copy client (simplified for read-only)
echo "Copying AAP client..."
cp "$SRC_REPO/src/aap_migration/client/aap_source_client.py" \
   "$DEST_REPO/src/aap_migration_planner/client/aap_client.py"

# Copy utilities
echo "Copying utilities..."
cp "$SRC_REPO/src/aap_migration/utils/logging.py" \
   "$DEST_REPO/src/aap_migration_planner/utils/logging.py"

echo "Files copied. Now refactoring imports..."

# Refactor imports in all Python files
find "$DEST_REPO/src" -name "*.py" -type f -exec sed -i '' \
  -e 's/from aap_migration\./from aap_migration_planner./g' \
  -e 's/import aap_migration\./import aap_migration_planner./g' \
  -e 's/aap_source_client/aap_client/g' \
  -e 's/AAPSourceClient/AAPClient/g' \
  -e 's/dependency_graph/graph/g' \
  -e 's/reports\.py/text_report/g' \
  {} \;

echo "Import refactoring complete!"
echo "Extraction finished successfully."
