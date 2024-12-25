from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from agents.customer_support_multiagent.tools.excursion_tools import ExcursionTools
from agents.customer_support_multiagent.tools.extra_tools import CompleteOrEscalate
from agents.customer_support_multiagent.state import State
from langgraph.prebuilt import tools_condition
from langgraph.constants import END
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4-turbo-preview")

book_excursion_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized assistant for handling trip recommendations. "
            "The primary assistant delegates work to you whenever the user needs help booking a recommended trip. "
            "Search for available trip recommendations based on the user's preferences and confirm the booking details with the customer. "
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " Remember that a booking isn't completed until after the relevant tool has successfully been used."
            "\nCurrent time: {time}."
            '\n\nIf the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.'
            "\n\nSome examples for which you should CompleteOrEscalate:\n"
            " - 'nevermind i think I'll book separately'\n"
            " - 'i need to figure out transportation while i'm there'\n"
            " - 'Oh wait i haven't booked my flight yet i'll do that first'\n"
            " - 'Excursion booking confirmed!'",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)


book_excursion_safe_tools = [ExcursionTools.search_trip_recommendations]
book_excursion_sensitive_tools = [ExcursionTools.book_excursion, ExcursionTools.update_excursion, ExcursionTools.cancel_excursion]
book_excursion_tools = book_excursion_safe_tools + book_excursion_sensitive_tools
book_excursion_runnable = book_excursion_prompt | llm.bind_tools(
    book_excursion_tools + [CompleteOrEscalate]
)

def route_book_excursion(
            state: State,
        ):
            route = tools_condition(state)
            if route == END:
                return END
            tool_calls = state["messages"][-1].tool_calls
            did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
            if did_cancel:
                return "leave_skill"
            tool_names = [t.name for t in book_excursion_safe_tools]
            if all(tc["name"] in tool_names for tc in tool_calls):
                return "book_excursion_safe_tools"
            return "book_excursion_sensitive_tools"





