from dataclasses import dataclass

from langgraph.graph.state import CompiledStateGraph

from agents.bg_task_agent.bg_task_agent import bg_task_agent
from agents.chatbot import chatbot
from agents.research_assistant import research_assistant
from agents.customer_support_multiagent import customer_support
from schema import AgentInfo

DEFAULT_AGENT = "customer-support-agent"


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


agents: dict[str, Agent] = {
    "chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    "research-assistant": Agent(
        description="A research assistant with web search and calculator.", graph=research_assistant
    ),
    "bg-task-agent": Agent(description="A background task agent.", graph=bg_task_agent),
    "customer-support-agent": Agent(description="Example with human-in-the-loop", graph=customer_support),
}


def get_agent(agent_id: str) -> CompiledStateGraph:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]