from managed_deepagents import define_deep_agent
from tools.jev_classifier import classify_gap
from tools.progress import set_stage

agent = define_deep_agent(
    name="korvai-audit-pm",
    model="openai:gpt-5.6-terra",
    tools=[classify_gap,set_stage],
)
