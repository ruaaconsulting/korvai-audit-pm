#!/usr/bin/env python3
"""
IEM-PM Knowledge Index Derivation
Scans knowledge/ directories and builds a machine-readable index.
Run this whenever standards are added, removed, or reorganized.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    from paths import ENGINE_DIR, KNOWLEDGE_DIR
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from paths import ENGINE_DIR, KNOWLEDGE_DIR

INDEX_PATH = ENGINE_DIR / "knowledge_index.json"


def scan_knowledge_base() -> dict:
    """
    Scans knowledge/ subdirectories and builds an index.
    Does not read file contents — only catalogs what is available.
    """
    index = {
        "index_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "knowledge_dir": str(KNOWLEDGE_DIR.relative_to(ENGINE_DIR.parent)),
        "categories": {},
        "total_documents": 0,
        "total_bytes": 0
    }

    if not KNOWLEDGE_DIR.exists():
        print("WARNING: knowledge/ directory does not exist.")
        return index

    for category_dir in sorted(KNOWLEDGE_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        category = category_dir.name
        files = []

        for doc in sorted(category_dir.rglob("*")):
            if not doc.is_file():
                continue
            if doc.name in [".gitkeep", ".gitignore", "README.md"]:
                continue

            stat = doc.stat()
            files.append({
                "filename": doc.name,
                "relative_path": str(doc.relative_to(KNOWLEDGE_DIR)),
                "size_bytes": stat.st_size,
                "extension": doc.suffix.lower(),
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            })

        if files:
            index["categories"][category] = {
                "document_count": len(files),
                "documents": files
            }
            index["total_documents"] += len(files)
            index["total_bytes"] += sum(f["size_bytes"] for f in files)

    return index


def main():
    index = scan_knowledge_base()

    # Write index
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")

    # Summary
    print(f"Knowledge index written: {INDEX_PATH}")
    print(f"  Categories: {len(index['categories'])}")
    print(f"  Total documents: {index['total_documents']}")
    print(f"  Total size: {index['total_bytes']:,} bytes")

    for cat, data in index["categories"].items():
        print(f"  - {cat}: {data['document_count']} document(s)")


if __name__ == "__main__":
    main()