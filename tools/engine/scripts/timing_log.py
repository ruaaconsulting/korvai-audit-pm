"""Stage timing log (SKILL.md §6.9) -- shared by manifest_to_findings.py (Stage 8) and
render.py (Stage 9), the two stages that log their own entry/exit automatically instead of
relying on the LLM's Bash-based logging used for Stages 0-7.

Deliberately best-effort: a timing.log write failure (disk full, permissions) must never
block the actual pipeline it's instrumenting. This is diagnostic-only, never load-bearing.

Known scope limit: this file is meant to live in one place per audit -- the project's own
`reports/` folder, same location for the Manifest, JSON, HTML, and TXT (the default,
recommended path for both scripts, and the only path SKILL.md ever instructs the LLM to use).
If an operator explicitly overrides `--output`/`--output-html`/`--output-txt` to redirect a
stage's file to a *different* directory than the Manifest's own folder, that stage's
entry/exit lines land in a second, separate timing.log next to wherever it was redirected to
-- the timing record splits across two files and `append_audit_end_summary()`'s total will
be inaccurate for that run. Not handled automatically; keep outputs co-located if you want an
accurate total.
"""
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_TIMESTAMP_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_stage(reports_dir: Path, label: str, event: str) -> None:
    """Append one '[label] event timestamp' line to <reports_dir>/timing.log."""
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        with open(reports_dir / "timing.log", "a", encoding="utf-8") as f:
            f.write(f"[{label}] {event} {_now_iso()}\n")
    except OSError:
        pass


def _last_timestamp(lines: list, prefix: str) -> Optional[datetime]:
    """Last (most recent) timestamp on a line starting with `prefix`, or None if no match."""
    found = None
    for line in lines:
        if line.startswith(prefix):
            m = _TIMESTAMP_RE.search(line)
            if m:
                found = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return found


def append_audit_end_summary(reports_dir: Path) -> None:
    """Called once, at the very end of Stage 9. Anchors to THIS run's start, then appends a
    total-elapsed summary line.

    timing.log is append-only across every audit run of a project (SKILL.md §6.9, by design,
    so timing trends are visible over time) -- so on any run after the first, the file
    contains timestamps from prior runs too. Using the file's global earliest timestamp would
    silently report a multi-run total instead of this run's. Instead, anchor to the most
    recent '=== AUDIT START ===' line (written once, by Stage 0, at the actual start of THIS
    run), falling back to this run's own Stage 8 entry only if Stages 0-7 never ran in this
    session (e.g. the scripts invoked standalone, without the LLM stages).

    If timing.log doesn't exist or has no parseable start marker -- e.g. an operator ran
    render.py by hand against an old JSON with no matching log -- this silently does nothing
    rather than fabricate a start time.
    """
    log_path = reports_dir / "timing.log"
    if not log_path.exists():
        return
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
        start = _last_timestamp(lines, "=== AUDIT START") or _last_timestamp(
            lines, "[Stage 8 Findings JSON] ENTRY"
        )
        if start is None:
            return
        end = datetime.now(timezone.utc)
        total_seconds = int((end - start).total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"=== AUDIT END | {_now_iso()} | TOTAL: {total_seconds}s ({minutes}m {seconds}s) ===\n"
            )
    except (OSError, ValueError):
        pass
