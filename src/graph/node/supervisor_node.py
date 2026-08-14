
from datetime import datetime

from src.graph.state.UnderwritingState import UnderwritingState
from src.utils.helper_functions import sanitize_pii


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
    try:
        if not isinstance(state, dict):
            raise TypeError("Supervisor received a non-dictionary state.")

        analyses_done = {
            "credit": bool(state.get("credit_analysis")),
            "income": bool(state.get("income_analysis")),
            "asset": bool(state.get("asset_analysis")),
            "collateral": bool(state.get("collateral_analysis"))
        }

        if not analyses_done["credit"]:
            next_agent = "credit"
        elif not analyses_done["income"]:
            next_agent = "income"
        elif not analyses_done["asset"]:
            next_agent = "asset"
        elif not analyses_done["collateral"]:
            next_agent = "collateral"
        else:
            next_agent = "critic"

        return {
            **state,
            "next_agent": next_agent,
            "analysis_complete": all(analyses_done.values())
        }
    except Exception as exc:
        fallback_state = dict(state) if isinstance(state, dict) else {}
        fallback_state.update({
            "next_agent": "credit",
            "analysis_complete": False,
            "reasoning_chain": fallback_state.get("reasoning_chain", []) + [
                f"Supervisor: Routing error recovered: {exc}"
            ]
        })
        return fallback_state

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