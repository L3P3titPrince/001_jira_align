# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jira Align data extraction and visualization tool that connects to the Anaplan/Jira Align REST API to extract hierarchical project data (Initiatives/Epics, Features, Dependencies, Ideas), enriches it with related titles and user info, exports it as CSV, and generates interactive HTML visualizations.

## Environment Setup

Python is installed via pyenv (required due to corporate restrictions on package managers and brew):

```bash
# Activate the existing virtual environment
source venv/bin/activate
```

Required packages: `requests`, `pandas`, `flask`, `dash`, `plotly`

The project uses Python 3.9 (from `venv/`) but the README documents a 3.11.7 install path for new setups.

## Running the Application

All scripts run from the `src/` directory:

```bash
cd src

# Flask web UI (primary interface) — http://127.0.0.1:5000/
python app.py

# Extract epics with enriched release/feature titles (CLI)
python epic_extract_01.py

# Extract epics + features + dependencies as separate CSVs (CLI)
python epic_extract.py

# Extract ideas with status/group mapping
python idea_extract.py

# Generate Sankey visualization (saves to /output/*.html)
python sankey_diagram_04.py

# Interactive Dash dashboard — http://127.0.0.1:8050/
python dashboard.py
```

## Architecture

### Module Responsibilities

| Module | Role |
|---|---|
| `config.py` | `JIRA_ALIGN_URL` and `API_TOKEN` — **never commit this file** |
| `api_client.py` | `get_align_data()` (single request), `get_paged_align_data()` (paginated with OData `$filter`/`$select`/`$top`/`$skip`) |
| `enrichment.py` | Batch-fetches related entities (releases, features, users, ideas) and returns `{id: title}` maps |
| `cache_manager.py` | Wraps user API calls with a 30-day CSV cache at `data/user_cache.csv` |
| `epic_extract_01.py` | Main pipeline: builds OData filter → paged API call → enrich with release/feature titles → save CSV |
| `epic_extract.py` | Alternative pipeline: extracts Epics → Features → Dependencies as three separate relational CSVs |
| `idea_extract.py` | Ideas pipeline: loads `data/idea_status_mapping.csv` and `data/group_mapping.csv`, then enriches via API |
| `data_processor.py` | `save_to_csv()` — converts DataFrame to CSV under `data/` with optional column renaming |
| `app.py` | Flask UI: `GET /` serves form, `POST /extract` accepts `{"programs": [...], "releases": [...]}` JSON |
| `data_loader.py` | `prepare_sankey_data()` — joins initiatives/features/dependencies into a master table |
| `dashboard.py` | Dash app for interactive Epic → Feature → Dependencies navigation |

### Data Flow

```
Flask UI / CLI script
    → epic_extract_01.run_extraction_pipeline(programs, releases)
        → api_client.get_paged_align_data("/Epics", odata_filter)  ← config.py credentials
        → enrichment.get_release_titles_map(release_ids)
        → enrichment.get_feature_titles_map(feature_ids)
        → enrichment.get_user_map_with_cache()  ← cache_manager (30-day TTL)
        → data_processor.save_to_csv(df, "fully_enriched_epics_with_ids.csv")
    → data/ CSV files
        → sankey_diagram*.py / dashboard.py → output/ HTML visualizations
```

### OData Filtering Pattern

API calls use OData syntax for server-side filtering:

```python
# Program filter
"(primaryProgramId eq 72 or primaryProgramId eq 79)"

# Release filter (array membership)
"((releaseIds/any(r: r eq 54)) or (releaseIds/any(r: r eq 55)))"

# Pagination
params = {'$filter': filter, '$select': fields, '$top': 100, '$skip': skip}
```

Pagination loops until an empty response is returned.

### Hardcoded IDs (in epic_extract.py / epic_extract_01.py)

- Program IDs: 72 (Supply Chain), 79 (Workforce), 70 (Sales), 71 (Finance)
- Release IDs: 54–57 (2026 Q1–Q4)

These can be overridden via the Flask UI's `POST /extract` JSON body.

## File Locations

- Source code: `src/`
- Generated CSVs: `data/`
- HTML visualizations: `output/`
- Legacy/unused scripts: `deprecated/`
- API reference: https://anaplan.jiraalign.com/rest/align/api/docs/index.html
