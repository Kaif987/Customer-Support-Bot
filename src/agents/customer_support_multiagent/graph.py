from langgraph.graph import StateGraph, START
from agents.customer_support_multiagent.state import State
from agents.customer_support_multiagent.nodes import Nodes, Assistant
from agents.customer_support_multiagent.utility import update_dates
from langgraph.checkpoint.memory import MemorySaver
from agents.customer_support_multiagent.utility import create_entry_node, create_tool_node_with_fallback
from agents.customer_support_multiagent.assistants.flight_booking_assistant import update_flight_runnable, update_flight_sensitive_tools, update_flight_safe_tools, pop_dialog_state, route_update_flight
from agents.customer_support_multiagent.assistants.car_rental_assistant import book_car_rental_runnable, book_car_rental_sensitive_tools, book_car_rental_safe_tools, route_book_car_rental
from agents.customer_support_multiagent.assistants.hotel_assistant import book_hotel_runnable, book_hotel_sensitive_tools, book_hotel_safe_tools, route_book_hotel
from agents.customer_support_multiagent.assistants.excursion_assistant import book_excursion_runnable, book_excursion_sensitive_tools, book_excursion_safe_tools, route_book_excursion
from agents.customer_support_multiagent.assistants.primary_assistant import assistant_runnable, primary_assistant_tools, route_primary_assistant, route_to_workflow
from langgraph.constants import END
from core import settings
import os


class Workflow:
    local_file = "./agents/customer_support_multiagent/travel2.sqlite"
    backup_file = "./agents/customer_support_multiagent/travel2.backup.sqlite"

    if(settings.is_dev()):
        local_file = "./src/agents/customer_support_multiagent/travel2.sqlite"
        # The backup lets us restart for each tutorial section
        backup_file = "./src/agents/customer_support_multiagent/travel2.backup.sqlite"

    def __init__(self):
        if not os.path.exists(self.local_file):
            raise FileNotFoundError(f"Local file not found {self.local_file}")

        if not os.path.exists(self.backup_file):
            raise FileNotFoundError(f"Backup file not found {self.backup_file}")

        self.db = update_dates(backup_file=self.backup_file, file=self.local_file) 
        # create graph
        workflow = StateGraph(State)
        nodes = Nodes(self.db)

        # add nodes
        workflow.add_node("fetch_user_info", nodes.user_info)
        workflow.add_edge(START, "fetch_user_info")

        # Flight booking assistant
        workflow.add_node(
            "enter_update_flight",
            create_entry_node("Flight Updates & Booking Assistant", "update_flight"),
        )

        workflow.add_node("update_flight", Assistant(update_flight_runnable))
        workflow.add_edge("enter_update_flight", "update_flight")
        workflow.add_node(
            "update_flight_sensitive_tools",
            create_tool_node_with_fallback(update_flight_sensitive_tools),
        )

        workflow.add_node(
            "update_flight_safe_tools",
            create_tool_node_with_fallback(update_flight_safe_tools),
        )

        workflow.add_edge("update_flight_sensitive_tools", "update_flight")
        workflow.add_edge("update_flight_safe_tools", "update_flight")
        workflow.add_conditional_edges(
            "update_flight",
            route_update_flight,
            ["update_flight_sensitive_tools", "update_flight_safe_tools", "leave_skill", END],
        )

        workflow.add_node("leave_skill", pop_dialog_state)
        workflow.add_edge("leave_skill", "primary_assistant")

        # Car rental assistant
        workflow.add_node(
            "enter_book_car_rental",
            create_entry_node("Car Rental Assistant", "book_car_rental"),
        )
        workflow.add_node("book_car_rental", Assistant(book_car_rental_runnable))
        workflow.add_edge("enter_book_car_rental", "book_car_rental")
        workflow.add_node(
            "book_car_rental_safe_tools",
            create_tool_node_with_fallback(book_car_rental_safe_tools),
        )
        workflow.add_node(
            "book_car_rental_sensitive_tools",
            create_tool_node_with_fallback(book_car_rental_sensitive_tools),
        )

        workflow.add_edge("book_car_rental_sensitive_tools", "book_car_rental")
        workflow.add_edge("book_car_rental_safe_tools", "book_car_rental")
        workflow.add_conditional_edges(
            "book_car_rental",
            route_book_car_rental,
            [
                "book_car_rental_safe_tools",
                "book_car_rental_sensitive_tools",
                "leave_skill",
                END,
            ],
        )

        # Hotel booking assistant
        workflow.add_node(
            "enter_book_hotel", create_entry_node("Hotel Booking Assistant", "book_hotel")
        )
        workflow.add_node("book_hotel", Assistant(book_hotel_runnable))
        workflow.add_edge("enter_book_hotel", "book_hotel")
        workflow.add_node(
            "book_hotel_safe_tools",
            create_tool_node_with_fallback(book_hotel_safe_tools),
        )
        workflow.add_node(
            "book_hotel_sensitive_tools",
            create_tool_node_with_fallback(book_hotel_sensitive_tools),
        )


        workflow.add_edge("book_hotel_sensitive_tools", "book_hotel")
        workflow.add_edge("book_hotel_safe_tools", "book_hotel")
        workflow.add_conditional_edges(
            "book_hotel",
            route_book_hotel,
            ["leave_skill", "book_hotel_safe_tools", "book_hotel_sensitive_tools", END],
        )

        # Excursion assistant
        workflow.add_node(
            "enter_book_excursion",
            create_entry_node("Trip Recommendation Assistant", "book_excursion"),
        )
        workflow.add_node("book_excursion", Assistant(book_excursion_runnable))
        workflow.add_edge("enter_book_excursion", "book_excursion")
        workflow.add_node(
            "book_excursion_safe_tools",
            create_tool_node_with_fallback(book_excursion_safe_tools),
        )
        workflow.add_node(
            "book_excursion_sensitive_tools",
            create_tool_node_with_fallback(book_excursion_sensitive_tools),
        )

        workflow.add_edge("book_excursion_sensitive_tools", "book_excursion")
        workflow.add_edge("book_excursion_safe_tools", "book_excursion")
        workflow.add_conditional_edges(
            "book_excursion",
            route_book_excursion,
            ["book_excursion_safe_tools", "book_excursion_sensitive_tools", "leave_skill", END],
        )

        # Primary assistant
        workflow.add_node("primary_assistant", Assistant(assistant_runnable))
        workflow.add_node(
            "primary_assistant_tools", create_tool_node_with_fallback(primary_assistant_tools)
        )

        # The assistant can route to one of the delegated assistants,
        # directly use a tool, or directly respond to the user
        workflow.add_conditional_edges(
            "primary_assistant",
            route_primary_assistant,
            [
                "enter_update_flight",
                "enter_book_car_rental",
                "enter_book_hotel",
                "enter_book_excursion",
                "primary_assistant_tools",
                END,
            ],
        )
        workflow.add_edge("primary_assistant_tools", "primary_assistant")

        workflow.add_conditional_edges("fetch_user_info", route_to_workflow)


       # we don't need to direct to END node because we are using the tools_condition edge

        # The checkpointer lets the graph persist its state
        # this is a complete memory for the entire graph.
        memory = MemorySaver()

        self.app = workflow.compile(
            checkpointer=memory,
            # NEW: The graph will always halt before executing the "tools" node.
            # The user can approve or reject (or even alter the request) before
            # the assistant continues
            interrupt_before=[
                "update_flight_sensitive_tools",
                "book_car_rental_sensitive_tools",
                "book_hotel_sensitive_tools",
                "book_excursion_sensitive_tools",
            ],
)

customer_support = Workflow().app


