import json

from langchain.messages import HumanMessage, SystemMessage

from src.graph.state.UnderwritingState import UnderwritingState
from src.languagemodels.llmprovider import get_llm_instance
from src.rag.receiver import retrieve_relevant_policies
from src.tools.mortgage_tools import check_credit_score_policy
from src.utils.helper_functions import detect_bias_signals


def _normalize_app_data(app_data):
    if isinstance(app_data, dict):
        return app_data

    if isinstance(app_data, str):
        try:
            return json.loads(app_data)
        except json.JSONDecodeError:
            return {"raw_payload": app_data}

    return {}


def credit_analyst_node(state: UnderwritingState) -> UnderwritingState:
    """
    Analyzes borrower's credit profile and payment history.

    Evaluates:
    - Credit score quality
    - Payment history
    - Derogatory items (bankruptcies, foreclosures, collections)
    - Overall creditworthiness
    """

    policies = retrieve_relevant_policies(
        "credit score requirements bankruptcies foreclosures late payments"
    )

    # Get sanitized application data
    app_data = _normalize_app_data(state.get("sanitized_data", {}))

    # Use calculator tool for credit score assessment
    credit_score = app_data.get("credit_score", 0)
    credit_score_analysis = check_credit_score_policy.invoke({"credit_score": credit_score})

    # Build analysis prompt
    system_prompt = f"""
You are a Senior Credit Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

Your task is to analyze the borrower's credit profile and provide a detailed assessment.

ANALYSIS FRAMEWORK:
1. Credit Score Assessment - Use provided assessment (DO NOT recalculate)
2. Payment History - Review late payments and patterns
3. Derogatory Items - Evaluate bankruptcies, foreclosures, collections
4. Policy Compliance - Check against credit guidelines
5. Risk Rating - Assign credit risk (Low/Medium/High)
6. Recommendations - Provide conditions or concerns

Be thorough, objective, and policy-compliant. Support conclusions with data.
IMPORTANT: Use the EXACT credit score assessment provided below. Do not recalculate.
"""

    user_prompt = f"""
Analyze the credit profile for case {app_data.get('case_id')}:

CALCULATED CREDIT SCORE ASSESSMENT (ACCURATE - DO NOT RECALCULATE):
{credit_score_analysis}

CREDIT HISTORY DATA:
- Bankruptcies: {app_data.get('credit_history', {}).get('bankruptcies', 0)}
- Foreclosures: {app_data.get('credit_history', {}).get('foreclosures', 0)}
- Late Payments (12mo): {app_data.get('credit_history', {}).get('late_payments_12mo', 0)}
- Collections: {app_data.get('credit_history', {}).get('collections', [])}

Provide your detailed credit analysis based on the ACCURATE assessment above.
"""

    # Generate analysis using llm directly
    llm =  get_llm_instance("openai")  # Assuming this function returns an LLM instance
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # Extract analysis text
    analysis = response.content

    # Check for bias signals
    bias_flags = detect_bias_signals(analysis, app_data)

    # Update state
    return {
        **state,
        "credit_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Credit Analyst: Completed credit analysis for {app_data.get('case_id')}"
        ]
    }