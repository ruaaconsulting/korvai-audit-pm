import os, re, hashlib
from pathlib import Path

from langchain_typesafe import Choice, Noul, Score, TypeSafeClassifier
from langchain.tools import tool, ToolRuntime

# Get Threshold details from .env
raw = os.getenv("CONFIDENCE_THRESHOLD")
if raw is None:
    raise RuntimeError("CONFIDENCE_THRESHOLD not set in .env")

try:
    CONFIDENCE_THRESHOLD = float(raw)
except ValueError:
    raise ValueError(f"CONFIDENCE_THRESHOLD must be a valid decimal number, got: {raw}")

if not (0.0 <= CONFIDENCE_THRESHOLD <= 1.0):
    raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")

# ───────── Locate reference/ relative to this file ─────────
REFERENCE_DIR = Path(__file__).parent.parent / "reference"

# ───────── Helper: load one taxonomy file ─────────
def load_taxonomy(filename: str) -> dict:
    file_path = REFERENCE_DIR / filename
    text = file_path.read_text(encoding="utf-8")

    # 3a. Version line — case-insensitive to match "version: 1.0.0"
    version_match = re.search(r"^version:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    if not version_match:
        raise ValueError(f"{filename} has no Version: line")
    version = version_match.group(1).strip()

    # 3b. Fingerprint: catches edits made without a version bump
    fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

    # 3c. Criteria from numbered headings
    #     Handles all variants found in the actual files:
    #       ## 1 Missing — required information absent
    #       1 Missing — required information absent
    #       3. Disconnected — Information exists but is isolated
    #       3 Definition / Taxonomy — The data is captured but defined incorrectly
    criteria = {}
    pattern = re.compile(
        r"##\s+\s*\d+\.?\s+(.+?)\s+—\s+(.+)$",
        re.MULTILINE
    )
    for match in pattern.finditer(text):
        name = match.group(1).strip()
        definition = match.group(2).strip()
        criteria[name] = definition

    # 3d. Closed-taxonomy guard
    if len(criteria) != 7:
        raise ValueError(f"{filename}: expected 7 headings, found {len(criteria)}")

    return {
        "instructions": text,
        "criteria":     criteria,
        "version":      version,
        "fingerprint":  fingerprint,
    }

# ───────── Load both once, when the module loads ─────────
GAP_TYPES    = load_taxonomy("gap-taxonomy.md")
ROOT_ORIGINS = load_taxonomy("root-origins.md")


classifier = TypeSafeClassifier()

# ───────── helper 1: normalize text so formatting doesn't cause false rejections ─────────
def normalize(text: str) -> str:
    """
    Normalize text so that superficial formatting differences
    (dash types, curly quotes, whitespace) don't cause false rejections
    during the verbatim evidence check.
    """
    # All dash types become a single "-"
    text = text.replace("—", "-").replace("–", "-")

    # Curly quotes become straight quotes
    text = (text
            .replace("‘", "'").replace("’", "'")
            .replace("“", '"').replace("”", '"'))

    # Collapse every run of spaces/tabs/newlines into a single space
    text = re.sub(r"\s+", " ", text)

    # Trim spaces at both ends
    return text.strip()


# ───────── helper 2: collect everything the USER supplied ─────────
def supplied_text(runtime: ToolRuntime) -> str:
    """
    Collect every piece of text the user has supplied in this conversation:
      (a) human messages (plain text + multimodal text blocks)
      (b) uploaded files, if any (needed for Rung 6)
    Returns a single normalized string.
    """
    parts: list[str] = []

    # (a) pasted text: every human message in the conversation
    for message in runtime.state.get("messages", []):
        # LangChain messages expose .type ("human"/"ai"/...) or .type attribute
        msg_type = getattr(message, "type", None)
        if msg_type != "human":
            continue

        content = message.content
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            # Multimodal content blocks: [{"type": "text", "text": "..."}, ...]
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif hasattr(block, "text"):
                    parts.append(block.text)

    # (b) uploaded files, if any (skip gracefully if the key doesn't exist)
    files = runtime.state.get("files") if hasattr(runtime.state, "get") else None
    if files:
        for file in files:
            # Accept either a .text attribute or a dict with "text" key
            if hasattr(file, "text"):
                parts.append(file.text)
            elif isinstance(file, dict):
                parts.append(file.get("text", "") or file.get("content", ""))

    return normalize(" ".join(parts))

@tool(parse_docstring=True)
def classify_gap(requirement: str,
                 evidence: str,
                 expected: str,
                 observed: str,
                 runtime: ToolRuntime) -> dict:
    """
    Classify one audit finding into a gap type and root origin using Jev.
    The returned labels and confidence values are final and must be used
    exactly as returned.

    Args:
        requirement: The baseline clause, quoted exactly.
        evidence: An exact, unedited quote from the supplied evidence; no "..." and no trimming inside the quote.
        expected: What the clause requires, in a few words (e.g. "a named individual owner").
        observed: What the evidence shows, in a few words (e.g. "Owner: TBD").
    """
    # NOTE: runtime is injected by LangChain; the agent never sees or fills it.

    # 1. Verbatim check, BEFORE spending anything on Jev
    if normalize(evidence) not in supplied_text(runtime):
        return {
            "error": "evidence_not_verbatim",
            "message": ("The evidence is not an exact quote from the supplied material. "
                        "Copy it word for word, with no '...' and no edits, and call again."),
            "evidence_verified": False,
        }
        # do NOT call Jev
    
    variance = f"Required: {expected}. Observed: {observed}."

    # 1. The state Jev reads: the finding only
    state = { "requirement": requirement,
              "evidence":    evidence,
              "variance":    variance }

    # 2. One call, two questions, each carrying its full taxonomy document
    response = classifier.invoke(
        {
            "state": state,
            "questions": 
            {
                "gap_type": Choice
                            (
                                instructions= GAP_TYPES["instructions"],
                                criteria= GAP_TYPES["criteria"]
                            ),
                "root_origin": Choice
                            (
                                instructions= ROOT_ORIGINS["instructions"],
                                criteria= ROOT_ORIGINS["criteria"]
                            ),
            }
        }
    )

    gap = response.choices["gap_type"]
    root = response.choices["root_origin"]

    # 3. The threshold is decided in code, never by the agent
    needs_review = gap.confidence < CONFIDENCE_THRESHOLD or root.confidence < CONFIDENCE_THRESHOLD

    # 4. Return everything the agent must copy into the manifest
    return {
        "gap_type":                  gap.choice,
        "gap_type_definition":       GAP_TYPES["criteria"].get(gap.choice, ""),
        "gap_type_confidence":       gap.confidence,
        "gap_type_probabilities":    gap.probabilities,
        "root_origin":               root.choice,
        "root_origin_definition":    ROOT_ORIGINS["criteria"].get(root.choice, ""),
        "root_origin_confidence":    root.confidence,
        "root_origin_probabilities": root.probabilities,
        "needs_review":              needs_review,
        "threshold_used":            CONFIDENCE_THRESHOLD,
        "classified_by":             response.model,
        "taxonomy": {
            "gap_types": {
                "version": GAP_TYPES["version"],
                "fingerprint": GAP_TYPES["fingerprint"]
            },
            "root_origins": {
                "version": ROOT_ORIGINS["version"],
                "fingerprint": ROOT_ORIGINS["fingerprint"]
            },
        },
        "evidence_verified": True,
        "variance_sent":     variance,
    }