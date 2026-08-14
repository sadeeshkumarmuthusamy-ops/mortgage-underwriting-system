from langchain.messages import HumanMessage, SystemMessage

from src.graph.state.UnderwritingState import UnderwritingState
from src.languagemodels.llmprovider import get_llm_instance
from src.rag.receiver import retrieve_relevant_policies
from src.tools.mortgage_tools import calculate_reserves, check_large_deposits
from src.utils.helper_functions import detect_bias_signals


def asset_analyst_node(state: UnderwritingState) -> UnderwritingState:
    """
    Analyzes borrower's assets and reserves.

    Evaluates:
    - Down payment source and adequacy
    - Reserve funds for emergencies
    - Large deposit sourcing
    - Asset documentation
    """
    try:
        app_data = state.get("sanitized_data") or state.get("applicant_data") or {}
        if not isinstance(app_data, dict):
            app_data = {}

        assets = app_data.get('assets', {}) if isinstance(app_data.get('assets', {}), dict) else {}
        loan = app_data.get('loan', {}) if isinstance(app_data.get('loan', {}), dict) else {}
        employment = app_data.get('employment', {}) if isinstance(app_data.get('employment', {}), dict) else {}
        monthly_income = employment.get('monthly_income', 0) or 0

        liquid_assets = float(assets.get('checking', 0) or 0) + float(assets.get('savings', 0) or 0)
        monthly_payment = float(loan.get('estimated_payment', 0) or 0)

        try:
            policies = retrieve_relevant_policies(
                "down payment reserves assets large deposits gift funds"
            )
        except Exception:
            policies = "Policy retrieval unavailable; using local assessment only."

        try:
            reserves_result = calculate_reserves.invoke(
                {"liquid_assets": liquid_assets, "monthly_payment": monthly_payment}
            )
        except Exception:
            reserves_result = (
                f"Reserves check unavailable: liquid assets ${liquid_assets:,.2f}, "
                f"monthly payment ${monthly_payment:,.2f}."
            )

        try:
            deposits_result = check_large_deposits.invoke({
                "deposits": assets.get('recent_deposits', []),
                "monthly_income": monthly_income
            })
        except Exception:
            deposits_result = "Large deposit review unavailable."

        case_id = app_data.get('case_id') or state.get('case_id') or 'UNKNOWN'

        system_prompt = f"""
You are a Senior Asset Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

Your task is to analyze the borrower's assets and provide a detailed assessment.

ANALYSIS FRAMEWORK:
1. Down Payment Adequacy - Verify sufficient funds
2. Reserve Requirements - Use provided calculation
3. Large Deposits - Use provided analysis
4. Source of Funds - Ensure proper sourcing
5. Risk Assessment - Identify asset-related risks
6. Documentation Needs - List required documents

Be thorough, objective, and policy-compliant. Support conclusions with data.
IMPORTANT: Use the EXACT reserve calculation and large deposit analysis provided below. Do not recalculate.
"""

        user_prompt = f"""
Analyze the asset profile for case {case_id}:

ASSET DATA:
- Checking: ${float(assets.get('checking', 0) or 0):,.2f}
- Savings: ${float(assets.get('savings', 0) or 0):,.2f}
- 401k/Retirement: ${float(assets.get('retirement', 0) or 0):,.2f}
- Other Assets: {assets.get('other_assets', 'N/A')}
- Total Liquid Assets: ${liquid_assets:,.2f}

LOAN REQUIREMENTS:
- Required Down Payment: ${float(loan.get('down_payment', 0) or 0):,.2f}
- Estimated Monthly Payment (for reserves): ${monthly_payment:,.2f}

CALCULATED RESERVES (ACCURATE - DO NOT RECALCULATE):
{reserves_result}

LARGE DEPOSIT ANALYSIS (ACCURATE - DO NOT RECALCULATE):
{deposits_result}

Provide your detailed asset analysis based on the ACCURATE calculations and analyses above.
"""

        try:
            llm = get_llm_instance("openai")
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            analysis = getattr(response, "content", None) or (
                f"Asset review for case {case_id}: total liquid assets are ${liquid_assets:,.2f}. "
                f"Reserve check: {reserves_result}. Large deposit review: {deposits_result}."
            )
        except Exception:
            analysis = (
                f"Asset review for case {case_id}: total liquid assets are ${liquid_assets:,.2f}. "
                f"Reserve check: {reserves_result}. Large deposit review: {deposits_result}. "
                "Additional documentation may be required for asset verification."
            )

        bias_flags = detect_bias_signals(analysis, app_data)

        return {
            **state,
            "asset_analysis": analysis,
            "bias_flags": state.get("bias_flags", []) + bias_flags,
            "reasoning_chain": state.get("reasoning_chain", []) + [
                f"Asset Analyst: Completed asset analysis and deposit review for {case_id}"
            ]
        }
    except Exception as exc:
        fallback_analysis = (
            "Asset analysis could not be completed due to a processing error. "
            "The file was retained for manual review."
        )
        return {
            **state,
            "asset_analysis": fallback_analysis,
            "bias_flags": state.get("bias_flags", []),
            "reasoning_chain": state.get("reasoning_chain", []) + [
                f"Asset Analyst: Error during asset review: {exc}"
            ]
        }