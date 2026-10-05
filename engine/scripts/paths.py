"""Single source of truth for repo-relative paths.

Every path here is anchored to this file's own location, not the caller's
cwd, so scripts behave the same whether invoked as `python scripts/foo.py`
or `cd scripts && python foo.py`. This is deliberately just path arithmetic
-- no logic, no I/O -- so it stays trivial to keep correct if the repo
layout ever changes during packaging (edit this one file, not four).
"""
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent      # skills/intelligence-engine/scripts/
ENGINE_DIR = SCRIPTS_DIR.parent                    # skills/intelligence-engine/
REPO_ROOT = ENGINE_DIR.parent.parent                # repository root

KNOWLEDGE_DIR = ENGINE_DIR / "knowledge"
REGISTRIES_DIR = ENGINE_DIR / "registries"
ASSETS_DIR = ENGINE_DIR / "assets"
# No single REPORTS_DIR: reports are written into a `reports/` folder that is
# always a sibling of the `evidence/` folder for the project being audited
# (e.g. `Audit/<Project>/reports/`, sibling to `Audit/<Project>/evidence/`).
# Each script derives this from its own input path -- see manifest_to_findings.py
# and render.py, which default their output next to the file they were given.
DEFAULT_TEMPLATE = ASSETS_DIR / "report_template.html"
DEFAULT_SCOPE_LIMITATION_TEMPLATE = ASSETS_DIR / "scope_limitation_template.html"
