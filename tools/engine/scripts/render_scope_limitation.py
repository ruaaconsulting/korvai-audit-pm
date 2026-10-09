#!/usr/bin/env python3
"""
IEM-PM Scope Limitation Notice Renderer
Reads a Scope Limitation Notice (markdown, written by the LLM on Halt Condition 6 --
see SKILL.md Section 6.6 and references/evidence-sufficiency.md) and renders the HTML
counterpart from assets/scope_limitation_template.html.

No canonical JSON step: evidence-sufficiency.md (c) is explicit that a halted audit
emits no findings data, so this script parses the .md directly to .html -- there is
no equivalent of manifest_to_findings.py in this path.
"""

import re
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

from jinja2 import Template

try:
    from paths import DEFAULT_SCOPE_LIMITATION_TEMPLATE
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from paths import DEFAULT_SCOPE_LIMITATION_TEMPLATE

CATEGORY_LETTERS = {"A", "B", "C", "D", "E", "F", "G"}

SECTION_HEADING = re.compile(r'^##\s*(\d+)\.\s*.+?\s*$', re.MULTILINE)
TABLE_ROW = re.compile(r'^\|(.+)\|\s*$', re.MULTILINE)
TABLE_SEPARATOR = re.compile(r'^\|[\s:|-]+\|$')
CATEGORY_CELL = re.compile(r'^([A-G])\s*—\s*(.+)$')
FAILURE_BULLET = re.compile(r'-\s*\*\*([A-G])\s*—[^*]*\*\*:\s*(.*?)(?=\n-\s*\*\*[A-G]\s*—|\Z)', re.DOTALL)
NUMBERED_ITEM = re.compile(r'^\d+\.\s+(.*?)(?=\n\d+\.\s|\Z)', re.DOTALL | re.MULTILINE)
BULLET_ITEM = re.compile(r'^-\s+(.*?)(?=\n-\s|\Z)', re.DOTALL | re.MULTILINE)


class NoticeParseError(Exception):
    pass


class NoticeParser:
    """Parses a Scope Limitation Notice markdown file into the Jinja2 context
    assets/scope_limitation_template.html expects (see evidence-sufficiency.md,
    Template Context table)."""

    def __init__(self, notice_path: Path):
        self.notice_path = notice_path
        self.raw = notice_path.read_text(encoding="utf-8")
        self.errors: List[str] = []

    def parse(self) -> Dict[str, Any]:
        frontmatter = self._parse_frontmatter()
        sections = self._split_sections()

        for required in ("notice_id", "generated_at", "artifact_count"):
            if required not in frontmatter:
                self.errors.append(f"[E-NOTICE-002] Frontmatter missing required field '{required}'")

        for num, label in ((1, "Executive Summary"), (4, "Professional Opinion"), (6, "Next Step")):
            if not sections.get(num, "").strip():
                self.errors.append(f"[E-NOTICE-004] Section {num} ({label}) is missing or empty")

        categories = self._parse_categories(sections.get(2, ""))
        if len(categories) != 7:
            self.errors.append(
                f"[E-NOTICE-003] Coverage Analysis table must list exactly 7 categories (A-G); "
                f"found {len(categories)}"
            )
        self._apply_failure_reasons(categories, sections.get(3, ""))

        recommendations = self._parse_list(sections.get(5, ""))

        try:
            artifact_count = int(frontmatter.get("artifact_count", 0))
        except ValueError:
            artifact_count = 0

        standards = frontmatter.get("standards_declared", [])
        if isinstance(standards, str):
            standards = [standards]

        return {
            "notice": {
                "audit_id": frontmatter.get("notice_id", "unknown"),
                "standards_declared": standards,
                "executive_summary": sections.get(1, "").strip(),
                "artifact_count": artifact_count,
                "professional_opinion": sections.get(4, "").strip(),
                "recommendations": recommendations,
                "next_step": sections.get(6, "").strip(),
            },
            "categories": categories,
            "generated_at": frontmatter.get("generated_at", ""),
        }

    def validate(self) -> List[str]:
        return self.errors

    # ─── Frontmatter ───

    def _parse_frontmatter(self) -> Dict[str, Any]:
        match = re.match(r'^---\n(.*?)\n---\n', self.raw, re.DOTALL)
        if not match:
            self.errors.append("[E-NOTICE-002] No YAML frontmatter block found")
            return {}

        data: Dict[str, Any] = {}
        lines = match.group(1).split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            kv = re.match(r'^(\w+):\s*(.*)$', line)
            if not kv:
                i += 1
                continue
            key, value = kv.group(1), kv.group(2).strip()
            if value:
                data[key] = value
                i += 1
                continue
            # Blank value -- check for a following '  - item' list block.
            items = []
            j = i + 1
            while j < len(lines) and re.match(r'^\s+-\s+', lines[j]):
                items.append(re.sub(r'^\s+-\s+', '', lines[j]).strip())
                j += 1
            data[key] = items if items else ""
            i = j
        return data

    # ─── Section splitting ───

    def _split_sections(self) -> Dict[int, str]:
        matches = list(SECTION_HEADING.finditer(self.raw))
        sections: Dict[int, str] = {}
        for idx, m in enumerate(matches):
            num = int(m.group(1))
            start = m.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(self.raw)
            body = re.split(r'\n---\n', self.raw[start:end])[0]
            sections[num] = body.strip()
        return sections

    # ─── Coverage Analysis table (Section 2) ───

    def _parse_categories(self, section_text: str) -> List[Dict[str, Any]]:
        rows = [m.group(1) for m in TABLE_ROW.finditer(section_text)]
        rows = [r for r in rows if not TABLE_SEPARATOR.match(f"|{r}|")]
        if rows:
            rows = rows[1:]  # drop the header row

        categories = []
        for row in rows:
            cells = [c.strip() for c in row.split("|")]
            if len(cells) < 4:
                continue
            cat_cell, domain, status_cell, artifacts_cell = cells[0], cells[1], cells[2], cells[3]

            cell_match = CATEGORY_CELL.match(cat_cell)
            if not cell_match:
                continue
            letter, name_raw = cell_match.group(1), cell_match.group(2)
            mandatory = "mandatory" in name_raw.lower()
            name = re.sub(r'\*?\(Mandatory\)\*?', '', name_raw, flags=re.IGNORECASE).strip(" *")

            status_clean = status_cell.replace("*", "").strip()
            present = status_clean.lower().startswith("present")

            artifacts_clean = artifacts_cell.strip()
            artifacts = [] if artifacts_clean in ("—", "-", "") else [
                a.strip() for a in artifacts_clean.split(",") if a.strip()
            ]

            categories.append({
                "letter": letter,
                "name": name,
                "domain": domain,
                "mandatory": mandatory,
                "present": present,
                "artifacts": artifacts,
                "failure_reason": "",
            })
        return categories

    # ─── Mandatory Failures (Section 3) ───

    def _apply_failure_reasons(self, categories: List[Dict[str, Any]], section_text: str) -> None:
        by_letter = {c["letter"]: c for c in categories}
        for match in FAILURE_BULLET.finditer(section_text):
            letter, reason = match.group(1), match.group(2)
            if letter in by_letter:
                by_letter[letter]["failure_reason"] = re.sub(r'\s+', ' ', reason).strip()

    # ─── Recommendation (Section 5) ───

    def _parse_list(self, section_text: str) -> List[str]:
        items = [re.sub(r'\s+', ' ', m.group(1)).strip() for m in NUMBERED_ITEM.finditer(section_text)]
        if not items:
            items = [re.sub(r'\s+', ' ', m.group(1)).strip() for m in BULLET_ITEM.finditer(section_text)]
        return items


def load_template(template_path: Path) -> Template:
    with open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def main():
    parser = argparse.ArgumentParser(description="IEM-PM: Scope Limitation Notice (md) -> HTML")
    parser.add_argument("--notice", required=True, type=Path, help="Path to the Scope Limitation Notice markdown")
    parser.add_argument(
        "--template", type=Path, default=None,
        help=f"Path to HTML template. Defaults to {DEFAULT_SCOPE_LIMITATION_TEMPLATE.name}.",
    )
    parser.add_argument(
        "--output-html", type=Path, default=None,
        help="Output path for the HTML notice. Defaults to the --notice path with its "
             "extension swapped to .html (same stem, same directory -- see references/file-naming.md).",
    )
    args = parser.parse_args()

    if not args.notice.exists():
        print(f"[E-NOTICE-001] Scope Limitation Notice not found: {args.notice}")
        exit(1)

    notice_parser = NoticeParser(args.notice)
    context = notice_parser.parse()
    errors = notice_parser.validate()

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        exit(1)

    template_path = args.template or DEFAULT_SCOPE_LIMITATION_TEMPLATE
    output_html = args.output_html or args.notice.with_suffix(".html")

    template = load_template(template_path)
    html = template.render(**context)
    output_html.write_text(html, encoding="utf-8")

    print(f"HTML notice: {output_html}")
    print(f"Categories parsed: {len(context['categories'])}")
    print(f"Recommendations parsed: {len(context['notice']['recommendations'])}")


if __name__ == "__main__":
    main()
