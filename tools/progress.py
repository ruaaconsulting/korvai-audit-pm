from typing import Literal
from langchain.tools import tool

# The fixed list of methodology stages, in order.
# Literal means the agent can ONLY use these exact words.
Stage = Literal["baseline", "charter", "compare", "classify","severity", "score", "report"]



@tool(parse_docstring=True)
def set_stage(stage: Stage, note: str) -> dict:
    """
    Record that the audit is entering a methodology stage. Call this at the
    start of every stage, in methodology order, before doing that stage's work.

    Args:
        stage: The methodology stage being started.
        note: One short sentence describing what this stage will do in this audit.
    """

    return{
        "stage":  stage,
        "status": "started",
        "note":   note,
    }
