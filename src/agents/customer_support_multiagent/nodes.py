from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from agents.customer_support_multiagent.state import State
from langchain_openai import ChatOpenAI
from datetime import datetime
from agents.customer_support_multiagent.tools import HotelManagementTools, CarRentalTools, ExcursionTools, FlightManagementTools
from agents.customer_support_multiagent.utility import create_tool_node_with_fallback

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    async def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = await self.runnable.ainvoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


# llm = ChatOpenAI(model="gpt-4-turbo-preview")

# primary_assistant_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful customer support assistant for Swiss Airlines. "
#             " Use the provided tools to search for flights, company policies, and other information to assist the user's queries. "
#             " When searching, be persistent. Expand your query bounds if the first search returns no results. "
#             " If a search comes up empty, expand your search before giving up."
#             "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
#             "\nCurrent time: {time}.",
#         ),
#         ("placeholder", "{messages}"),
#     ]
# ).partial(time=datetime.now)

# part_1_tools = [
#     TavilySearchResults(max_results=1),
#     FlightManagementTools.fetch_user_flight_information,
#     FlightManagementTools.search_flights,
#     FlightManagementTools.lookup_policy,
#     FlightManagementTools.update_ticket_to_new_flight,
#     FlightManagementTools.cancel_ticket,
#     CarRentalTools.search_car_rentals,
#     CarRentalTools.book_car_rental,
#     CarRentalTools.update_car_rental,
#     CarRentalTools.cancel_car_rental,
#     HotelManagementTools.search_hotels,
#     HotelManagementTools.book_hotel,
#     HotelManagementTools.update_hotel,
#     HotelManagementTools.cancel_hotel,
#     ExcursionTools.search_trip_recommendations,
#     ExcursionTools.book_excursion,
#     ExcursionTools.update_excursion,
#     ExcursionTools.cancel_excursion,
# ]

# part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)



class Nodes:
    # assistant = Assistant(part_1_assistant_runnable)

    def __init__(self, db : str):
        self.db = db
        FlightManagementTools.initialize(self.db)
        HotelManagementTools.initialize(self.db)
        CarRentalTools.initialize(self.db)
        ExcursionTools.initialize(self.db)

    # def tools(self):

    #     part_1_tools = [
    #         TavilySearchResults(max_results=1),
    #         FlightManagementTools.fetch_user_flight_information,
    #         FlightManagementTools.search_flights,
    #         FlightManagementTools.lookup_policy,
    #         FlightManagementTools.update_ticket_to_new_flight,
    #         FlightManagementTools.cancel_ticket,
    #         CarRentalTools.search_car_rentals,
    #         CarRentalTools.book_car_rental,
    #         CarRentalTools.update_car_rental,
    #         CarRentalTools.cancel_car_rental,
    #         HotelManagementTools.search_hotels,
    #         HotelManagementTools.book_hotel,
    #         HotelManagementTools.update_hotel,
    #         HotelManagementTools.cancel_hotel,
    #         ExcursionTools.search_trip_recommendations,
    #         ExcursionTools.book_excursion,
    #         ExcursionTools.update_excursion,
    #         ExcursionTools.cancel_excursion,
    #     ]

    #     tools = create_tool_node_with_fallback(part_1_tools)
    #     return tools
    
    async def user_info(self, state: State, config: RunnableConfig):
        FlightManagementTools.initialize(self.db)
        info = await FlightManagementTools.fetch_user_flight_information.ainvoke({})
        return {"user_info": info} 
    
    