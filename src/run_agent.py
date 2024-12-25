import asyncio
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

load_dotenv()

from agents import DEFAULT_AGENT, agents  # noqa: E402

agent = agents["customer-support"]


async def main() -> None:
    inputs = {"messages": [("user", "What time is my flight ?")]}
    result = await agent.ainvoke(
        inputs,
        config=RunnableConfig(configurable={"thread_id": uuid4(), "passenger_id": "3442 587242"}),
    )
    result["messages"][-1].pretty_print()

    # Draw the agent graph as png
    # requires:
    # brew install graphviz
    # export CFLAGS="-I $(brew --prefix graphviz)/include"
    # export LDFLAGS="-L $(brew --prefix graphviz)/lib"
    # pip install pygraphviz
    #
    # agent.get_graph().draw_png("agent_diagram.png")


if __name__ == "__main__":
    asyncio.run(main())
