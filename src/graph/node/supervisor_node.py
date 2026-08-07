
from datetime import datetime

from graph.state.UnderwritingState import UnderwritingState
from utils.helper_functions import sanitize_pii


def initialize_application(state: UnderwritingState) -> UnderwritingState:
    """
    Initialize a new application with sanitized data.
    """
    # Sanitize PII
    sanitized = sanitize_pii(state["applicant_data"])

    return {
        **state,
        "sanitized_data": sanitized,
        "analysis_complete": False,
        "human_review_required": False,
        "human_review_completed": False,
        "bias_flags": [],
        "policy_violations": [],
        "reasoning_chain": [f"Application {state.get('case_id')} initialized"],
        "timestamp": datetime.now().isoformat()
    }

def supervisor_node(state: UnderwritingState) -> UnderwritingState:
    """
    Routes workflow to next agent or marks completion.
    """
    # Check which analyses are complete
    analyses_done = {
        "credit": state.get("credit_analysis") is not None,
        "income": state.get("income_analysis") is not None,
        "asset": state.get("asset_analysis") is not None,
        "collateral": state.get("collateral_analysis") is not None
    }

    # Route to first incomplete analysis
    if not analyses_done["credit"]:
        next_agent = "credit"
    elif not analyses_done["income"]:
        next_agent = "income"
    elif not analyses_done["asset"]:
        next_agent = "asset"
    elif not analyses_done["collateral"]:
        next_agent = "collateral"
    else:
        next_agent = "critic"  # All analyses complete

    return {
        **state,
        "next_agent": next_agent,
        "analysis_complete": all(analyses_done.values())
    }

def should_continue_to_agents(state: UnderwritingState) -> str:
    """
    Conditional routing: continue to agents or move to critic.
    """
    if state.get("analysis_complete", False):
        return "critic"
    return state.get("next_agent", "credit")

def check_human_review_required(state: UnderwritingState) -> str:
    """
    Determine if human review is needed.
    """
    if state.get("human_review_required", False):
        return "human_review"
    return "end"