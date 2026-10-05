"""Stage 0 mechanics: inventory knowledge/, extract TOC/bookmark skeletons,
fingerprint sources, and diff against the previous run.

Scope boundary (Principle 3 & 7): this script never reads body text and never
paraphrases. It hands the LLM a skeleton map (titles, section anchors, page
numbers) so Stage 0 can derive registry items from it. Interpretation stays
in SKILL.md.

Usage: python baseline.py
Exit code 0 + BASELINE_READY, or exit code 1 + BASELINE_ABSENT.
"""
import hashlib
import json
import sys
from pathlib import Path

try:
    from paths import KNOWLEDGE_DIR, REGISTRIES_DIR
    from derive_knowledge_index import scan_knowledge_base, INDEX_PATH
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from paths import KNOWLEDGE_DIR, REGISTRIES_DIR
    from derive_knowledge_index import scan_knowledge_base, INDEX_PATH

MANIFEST_PATH = REGISTRIES_DIR / "derivation_manifest.json"
SKELETON_PATH = REGISTRIES_DIR / "skeleton_map.json"


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_skeleton(path: Path) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))

    def walk(nodes, level=1):
        items = []
        for node in nodes:
            if isinstance(node, list):
                items.extend(walk(node, level + 1))
                continue
            try:
                page = reader.get_destination_page_number(node) + 1
            except Exception:
                page = None
            items.append({"title": str(node.title), "page": page, "level": level})
        return items

    try:
        return walk(reader.outline)
    except Exception:
        return []


def md_skeleton(path: Path) -> list[dict]:
    items = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            items.append({"title": line.lstrip("#").strip(), "page": i, "level": level})
    return items


def skeleton_for(path: Path) -> list[dict]:
    if path.suffix.lower() == ".pdf":
        return pdf_skeleton(path)
    if path.suffix.lower() == ".md":
        return md_skeleton(path)
    return []


def main() -> int:
    sources = sorted(
        p for p in KNOWLEDGE_DIR.rglob("*")
        if p.is_file() and p.name != "README.md"
    )
    if not sources:
        print(
            "[E-BASE-001] BASELINE_ABSENT — no standards found in knowledge/.\n"
            "IEM-PM ships no bundled standard text and never audits from assumption "
            "or model memory. Place the organization's real standards "
            "(PMI or organizational; PDF/MD) in skills/intelligence-engine/knowledge/ "
            "and re-run. No baseline, no audit."
        )
        return 1

    prev_manifest = json.loads(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
    prev_fingerprints = prev_manifest.get("fingerprints", {})
    prev_skeletons = (
        json.loads(SKELETON_PATH.read_text()) if SKELETON_PATH.exists() else {}
    )

    fingerprints, skeleton_map = {}, {}
    new_docs, changed_docs, reused_docs, unparseable = [], [], [], []

    for path in sources:
        doc_id = path.name
        try:
            fp = fingerprint(path)
        except Exception as e:
            unparseable.append({"document": doc_id, "reason": str(e)})
            continue
        fingerprints[doc_id] = fp

        # Only trust a cached skeleton if it's non-empty -- an empty list can mean
        # "no bookmarks" or "extraction failed last time"; retry rather than
        # freeze a stale failure in place until the source file itself changes.
        if (
            prev_fingerprints.get(doc_id) == fp
            and prev_skeletons.get(doc_id)
        ):
            skeleton_map[doc_id] = prev_skeletons[doc_id]
            reused_docs.append(doc_id)
            continue

        skeleton = skeleton_for(path)
        skeleton_map[doc_id] = skeleton
        (changed_docs if doc_id in prev_fingerprints else new_docs).append(doc_id)

    orphans = sorted(set(prev_fingerprints) - set(fingerprints))

    REGISTRIES_DIR.mkdir(exist_ok=True)
    SKELETON_PATH.write_text(json.dumps(skeleton_map, indent=2))
    MANIFEST_PATH.write_text(json.dumps(
        {"fingerprints": fingerprints, "orphans_removed": orphans}, indent=2
    ))

    # Folder/category index -- knowledge/'s actual subfolder structure, whatever
    # it's named. Never hardcode a fixed set of category names here or in
    # SKILL.md: the org is free to organize knowledge/ however it likes (see
    # SKILL.md Sec 13.2), and this index is how Stage 0 tells the rest of the
    # audit what categories actually exist this run, instead of assuming one.
    knowledge_index = scan_knowledge_base()
    INDEX_PATH.write_text(json.dumps(knowledge_index, indent=2))

    print(f"BASELINE_READY — {len(sources)} document(s) in knowledge/: "
          f"{len(reused_docs)} reused, {len(new_docs)} new, {len(changed_docs)} changed, "
          f"{len(orphans)} orphaned, {len(unparseable)} unparseable.")
    if new_docs:
        print(f"  new: {new_docs}")
    if changed_docs:
        print(f"  changed: {changed_docs}")
    if orphans:
        print(f"  orphans removed from manifest: {orphans}")
    if unparseable:
        print(f"  [E-BASE-002] unparseable (skipped, not guessed): {unparseable}")
    print(f"  skeleton_map -> {SKELETON_PATH}")
    print(f"  derivation_manifest -> {MANIFEST_PATH}")
    print(f"  knowledge_index ({len(knowledge_index['categories'])} categor"
          f"{'y' if len(knowledge_index['categories']) == 1 else 'ies'}) -> {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
