# @title 4.🏠 Collateral Analyst Agent Implementation

from graph.state import UnderwritingState
from rag.receiver import retrieve_relevant_policies
from src.tools.mortgage_tools import calculate_ltv_ratio
from utils.helper_functions import detect_bias_signals
from languagemodels.llmprovider import get_llm_instance
from langchain.messages import HumanMessage, SystemMessage


def collateral_analyst_node(state: UnderwritingState) -> UnderwritingState:
    """
    Analyzes property value and condition.

    Evaluates:
    - Property appraisal and value
    - Loan-to-Value ratio
    - Property condition and habitability
    - Collateral adequacy
    """
    policies = retrieve_relevant_policies(
        "appraisal property condition LTV collateral"
    )

    app_data = state["sanitized_data"]
    property_data = app_data.get('property', {})
    loan = app_data.get('loan', {})

    # Use calculator tool for accurate LTV calculation
    loan_amount = loan.get('amount', 0)
    appraised_value = property_data.get('appraised_value', 0)

    ltv_result = calculate_ltv_ratio.invoke({
        "loan_amount": loan_amount,
        "property_value": appraised_value
    })

    system_prompt = f"""
You are a Senior Collateral Analyst with expertise in property valuation.

RELEVANT POLICIES:
{policies}

Your task is to assess the property as collateral for the loan.

ANALYSIS FRAMEWORK:
1. Appraisal Review - Validate property value
2. LTV Calculation - Use provided calculation (DO NOT recalculate)
3. Property Condition - Evaluate habitability
4. Marketability - Consider market factors
5. Risk Assessment - Identify collateral risks
6. Recommendations - Note any concerns

IMPORTANT: Use the EXACT LTV calculation provided below. Do not recalculate.
"""

    user_prompt = f"""
Analyze property collateral for case {app_data.get('case_id')}:

PROPERTY:
- Type: {property_data.get('type')}
- Appraised Value: ${appraised_value:,.2f}
- Condition: {property_data.get('condition')}
- Use: {loan.get('use')}

LOAN:
- Loan Amount: ${loan_amount:,.2f}
- Down Payment: ${loan.get('down_payment', 0):,.2f}

CALCULATED LTV (ACCURATE - DO NOT RECALCULATE):
{ltv_result}

Provide your collateral analysis based on this ACCURATE calculation.
"""

    llm = get_llm_instance("openai")  # Assuming this function returns an LLM instance
    # Generate analysis using llm directly
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        **state,
        "collateral_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Collateral Analyst: Completed property analysis (LTV from tool)"
        ]
    }
