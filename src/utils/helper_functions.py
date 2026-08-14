from datetime import datetime
from typing import Any, Dict, List

from src.graph.state.UnderwritingState import UnderwritingState


def sanitize_pii(data: Dict[str, Any] | str) -> Dict[str, Any] | str:
    """Remove or redact personally identifiable information.

    Args:
        data: Raw application data or a plain string payload

    Returns:
        Sanitized data safe for LLM processing
    """
    if not isinstance(data, dict):
        return data

    sanitized = data.copy()

    # Redact SSN (keep last 4 digits)
    if 'ssn' in sanitized:
        ssn = sanitized['ssn']
        sanitized['ssn'] = f"***-**-{ssn[-4:]}" if len(ssn) >= 4 else "***-**-XXXX"

    # Replace full names with placeholders
    if 'name' in sanitized:
        sanitized['name'] = "[APPLICANT_NAME]"

    # Redact addresses
    if 'address' in sanitized:
        sanitized['address'] = "[ADDRESS]"

    # Mask phone numbers
    if 'phone' in sanitized:
        phone = sanitized['phone']
        sanitized['phone'] = f"***-***-{phone[-4:]}" if len(phone) >= 4 else "***-***-XXXX"

    return sanitized

def detect_bias_signals(analysis: str, applicant_data: Dict[str, Any]) -> List[str]:
    """Check for potential Fair Lending Act violations.

    Args:
        analysis: Agent's analysis text
        applicant_data: Applicant information

    Returns:
        List of detected bias flags
    """
    flags = []

    # Protected characteristics that shouldn't influence decisions
    protected_terms = [
        'race', 'color', 'religion', 'national origin',
        'sex', 'marital status', 'age', 'gender',
        'disability', 'familial status'
    ]

    # Check if analysis mentions protected characteristics
    analysis_lower = analysis.lower()
    for term in protected_terms:
        if term in analysis_lower:
            flags.append(f"Analysis mentions protected characteristic: {term}")

    # Check for zip code-based discrimination
    if 'zip' in applicant_data or 'zipcode' in applicant_data:
        if 'neighborhood' in analysis_lower or 'area' in analysis_lower:
            flags.append("Potential geographic bias - review for Fair Lending compliance")

    return flags

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

def sanitize_pii_node(state: UnderwritingState) -> UnderwritingState:
    """
    Node wrapper for PII sanitization.
    """
    return state