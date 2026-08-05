from typing import Annotated, Any, Dict, List, Optional, TypedDict
from numpy import append

class UnderwritingState(TypedDict):
    """The complete state of a loan application as it moves through the system."""

    # Application Information
    case_id: str
    applicant_data: Dict[str, Any]
    sanitized_data: Dict[str, Any]

    # Agent Analysis Results
    credit_analysis: Optional[str]
    income_analysis: Optional[str]
    asset_analysis: Optional[str]
    collateral_analysis: Optional[str]

    # Coordination & Decision
    critic_review: Optional[str]
    decision_memo: Optional[str]
    final_decision: Optional[str]  # APPROVED, DENIED, CONDITIONAL_APPROVAL
    risk_score: Optional[int]  # 0-100

    # Workflow Control
    next_agent: Optional[str]
    analysis_complete: bool
    human_review_required: bool
    human_review_completed: bool
    human_notes: Optional[str]

    # Compliance
    bias_flags: List[str]
    policy_violations: List[str]

    # Audit Trail
    reasoning_chain: Annotated[List[str], "append"]  # Accumulates all reasoning steps
    timestamp: str
