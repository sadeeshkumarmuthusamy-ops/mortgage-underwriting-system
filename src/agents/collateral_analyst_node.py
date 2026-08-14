from langchain.messages import HumanMessage, SystemMessage

from src.graph.state.UnderwritingState import UnderwritingState
from src.languagemodels.llmprovider import get_llm_instance
from src.rag.receiver import retrieve_relevant_policies
from src.tools.mortgage_tools import calculate_ltv_ratio
from src.utils.helper_functions import detect_bias_signals


def collateral_analyst_node(state: UnderwritingState) -> UnderwritingState:
    """
    Analyzes property value and condition.

    Evaluates:
    - Property appraisal and value
    - Loan-to-Value ratio
    - Property condition and habitability
    - Collateral adequacy
    """
    try:
        app_data = state.get("sanitized_data") or state.get("applicant_data") or {}
        if not isinstance(app_data, dict):
            app_data = {}

        property_data = app_data.get('property', {}) if isinstance(app_data.get('property', {}), dict) else {}
        loan = app_data.get('loan', {}) if isinstance(app_data.get('loan', {}), dict) else {}
        case_id = app_data.get('case_id') or state.get('case_id') or 'UNKNOWN'

        try:
            policies = retrieve_relevant_policies(
                "appraisal property condition LTV collateral"
            )
        except Exception:
            policies = "Policy retrieval unavailable; using local assessment only."

        loan_amount = float(loan.get('amount', 0) or 0)
        appraised_value = float(property_data.get('appraised_value', 0) or 0)

        try:
            ltv_result = calculate_ltv_ratio.invoke({
                "loan_amount": loan_amount,
                "property_value": appraised_value
            })
        except Exception:
            ltv_result = (
                f"LTV unavailable: loan amount ${loan_amount:,.2f}, "
                f"appraised value ${appraised_value:,.2f}."
            )

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
Analyze property collateral for case {case_id}:

PROPERTY:
- Type: {property_data.get('type')}
- Appraised Value: ${appraised_value:,.2f}
- Condition: {property_data.get('condition')}
- Use: {loan.get('use')}

LOAN:
- Loan Amount: ${loan_amount:,.2f}
- Down Payment: ${float(loan.get('down_payment', 0) or 0):,.2f}

CALCULATED LTV (ACCURATE - DO NOT RECALCULATE):
{ltv_result}

Provide your collateral analysis based on this ACCURATE calculation.
"""

        try:
            llm = get_llm_instance("openai")
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            analysis = getattr(response, "content", None) or (
                f"Collateral review for case {case_id}: loan amount ${loan_amount:,.2f}, "
                f"appraised value ${appraised_value:,.2f}. LTV result: {ltv_result}."
            )
        except Exception:
            analysis = (
                f"Collateral review for case {case_id}: loan amount ${loan_amount:,.2f}, "
                f"appraised value ${appraised_value:,.2f}. LTV result: {ltv_result}. "
                "Additional collateral documentation may be required."
            )

        bias_flags = detect_bias_signals(analysis, app_data)

        return {
            **state,
            "collateral_analysis": analysis,
            "bias_flags": state.get("bias_flags", []) + bias_flags,
            "reasoning_chain": state.get("reasoning_chain", []) + [
                f"Collateral Analyst: Completed property analysis for {case_id}"
            ]
        }
    except Exception as exc:
        fallback_analysis = (
            "Collateral analysis could not be completed due to a processing error. "
            "The file was retained for manual review."
        )
        return {
            **state,
            "collateral_analysis": fallback_analysis,
            "bias_flags": state.get("bias_flags", []),
            "reasoning_chain": state.get("reasoning_chain", []) + [
                f"Collateral Analyst: Error during collateral review: {exc}"
            ]
        }
