# @title 3.💰 Asset Analyst Agent Implementation

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
    policies = retrieve_relevant_policies(
        "down payment reserves assets large deposits gift funds"
    )

    app_data = state["sanitized_data"]
    assets = app_data.get('assets', {})
    loan = app_data.get('loan', {})
    monthly_income = app_data.get('employment', {}).get('monthly_income', 0)

    # Use calculator tools for accurate calculations
    liquid_assets = assets.get('checking', 0) + assets.get('savings', 0)
    monthly_payment = loan.get('estimated_payment', 0)

    reserves_result = calculate_reserves.invoke(
        {"liquid_assets": liquid_assets, "monthly_payment": monthly_payment}
    )

    deposits_result = check_large_deposits.invoke({
        "deposits": assets.get('recent_deposits', []),
        "monthly_income": monthly_income
    })

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
Analyze the asset profile for case {app_data.get('case_id')}:

ASSET DATA:
- Checking: ${assets.get('checking', 0):,.2f}
- Savings: ${assets.get('savings', 0):,.2f}
- 401k/Retirement: ${assets.get('retirement', 0):,.2f}
- Other Assets: {assets.get('other_assets', 'N/A')}
- Total Liquid Assets: ${liquid_assets:,.2f}

LOAN REQUIREMENTS:
- Required Down Payment: ${loan.get('down_payment', 0):,.2f}
- Estimated Monthly Payment (for reserves): ${monthly_payment:,.2f}

CALCULATED RESERVES (ACCURATE - DO NOT RECALCULATE):
{reserves_result}

LARGE DEPOSIT ANALYSIS (ACCURATE - DO NOT RECALCULATE):
{deposits_result}

Provide your detailed asset analysis based on the ACCURATE calculations and analyses above.
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
        "asset_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Asset Analyst: Completed asset analysis and deposit review"
        ]
    }