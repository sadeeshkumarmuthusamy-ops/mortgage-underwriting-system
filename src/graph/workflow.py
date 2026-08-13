
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

import src.agents.asset_analyst_node  # noqa: F401
import src.agents.collateral_analyst_node  # noqa: F401
import src.agents.credit_analyst_node  # noqa: F401
import src.agents.critic_agent_node  # noqa: F401
import src.agents.decision_agent_node  # noqa: F401
import src.agents.income_analyst_node  # noqa: F401
from src.graph.node.supervisor_node import initialize_application, should_continue_to_agents, supervisor_node
from src.graph.state.UnderwritingState import UnderwritingState

asset_analyst_node = src.agents.asset_analyst_node.asset_analyst_node
collateral_analyst_node = src.agents.collateral_analyst_node.collateral_analyst_node
credit_analyst_node = src.agents.credit_analyst_node.credit_analyst_node
critic_agent_node = src.agents.critic_agent_node.critic_agent_node
decision_agent_node = src.agents.decision_agent_node.decision_agent_node
income_analyst_node = src.agents.income_analyst_node.income_analyst_node

def create_workflow() -> StateGraph:
    """
    Creates a workflow for mortgage underwriting using a state graph.

    The workflow consists of:
    1. Initialization of the application
    2. Routing to specialist agents (Credit, Income, Asset, Collateral)
    3. Critic review for quality assurance
    4. Final decision synthesis by the Decision Agent
    """
    workflow = StateGraph(UnderwritingState)
    # Add all nodes
    workflow.add_node("initialize", initialize_application)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("credit", credit_analyst_node)
    workflow.add_node("income", income_analyst_node)
    workflow.add_node("asset", asset_analyst_node)
    workflow.add_node("collateral", collateral_analyst_node)
    workflow.add_node("critic", critic_agent_node)
    workflow.add_node("decision", decision_agent_node)

    # Define the flow
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "supervisor")

    # Conditional routing: supervisor decides which specialist agent runs next
    # The should_continue_to_agents function evaluates state and returns agent name
    # Dictionary maps returned agent names to their corresponding node destinations
    # **There are 5 Agents to be mapped here**
    workflow.add_conditional_edges(
        "supervisor", should_continue_to_agents, {
            "credit": "credit",
            "income": "income",
            "asset": "asset",
            "collateral": "collateral",
            "critic": "critic"
           }
        )

    # All specialist agents return to supervisor
    workflow.add_edge("credit", "supervisor")
    workflow.add_edge("income", "supervisor")
    workflow.add_edge("asset", "supervisor")
    workflow.add_edge("collateral", "supervisor")

    # Critic flows to decision
    workflow.add_edge("critic", "decision")

    # Decision goes to end
    workflow.add_edge("decision", END)

    # Compile with checkpointing (HITL removed for automated testing)
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    return graph