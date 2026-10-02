from managed_deepagents import define_deep_agent
from tools.jev_classifier import classify_gap
from tools.progress import set_stage
from tools.severity import rate_severity
from tools.conformance import check_criterion

agent = define_deep_agent(
    name="korvai-audit-pm",
    model="openai:gpt-5.6-terra",
    tools=[classify_gap,set_stage,rate_severity,check_criterion],
)
