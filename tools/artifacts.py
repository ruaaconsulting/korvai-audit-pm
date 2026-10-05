import hashlib

from langchain.tools import tool, ToolRuntime

from tools.jev_classifier import normalize, supplied_text


@tool(parse_docstring=True)
def artifact_checksum(artifact_id: str, artifact_text: str, runtime: ToolRuntime) -> dict:
    """
    Compute the real SHA-256 checksum of one supplied artifact, for the
    Manifest's Per-Artifact Evidence Log. Use the returned checksum exactly.

    Args:
        artifact_id: The artifact identifier, for example "ART-001".
        artifact_text: The artifact's complete text exactly as supplied, with no edits or omissions.
    """
    # The artifact must actually be part of what the user supplied
    normalized = normalize(artifact_text)
    if normalized not in supplied_text(runtime):
        return {
            "error": "artifact_not_verbatim",
            "message": "The artifact text must be copied exactly as supplied. Copy it in full and call again.",
        }

    return {
        "artifact_id": artifact_id,
        "checksum_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "checksum_basis": "SHA-256 of the supplied artifact text (whitespace normalized)",
    }