from langchain.messages import HumanMessage, SystemMessage

from src.graph.state.UnderwritingState import UnderwritingState
from src.languagemodels.llmprovider import get_llm_instance
from src.rag.receiver import retrieve_relevant_policies
from src.tools.mortgage_tools import (
    calculate_dti_ratio,
    calculate_housing_expense_ratio,
    calculate_total_debt_obligations,
)
from src.utils.helper_functions import detect_bias_signals


def income_analyst_node(state: UnderwritingState) -> UnderwritingState:
    """
    Analyzes borrower's income stability and capacity to repay.

    Evaluates:
    - Employment history and stability
    - Income sources and verification
    - Debt-to-Income ratio
    - Capacity for monthly payment
    """
    # Retrieve income policies
    policies = retrieve_relevant_policies(
        "employment income verification DTI ratio self-employed"
    )

    app_data = state["sanitized_data"]

    # Use calculator tools for accurate calculations
    debts = app_data.get('debts', {})
    proposed_payment = app_data.get('loan', {}).get('estimated_payment', 0)
    monthly_income = app_data.get('employment', {}).get('monthly_income', 0)

    # Calculate using tools (eliminates hallucinations)
    total_debt = sum(debts.values())
    dti_result = calculate_dti_ratio.invoke({
        "monthly_debt": total_debt + proposed_payment,
        "monthly_income": monthly_income
    })

    housing_ratio_result = calculate_housing_expense_ratio.invoke({
        "monthly_payment": proposed_payment,
        "monthly_income": monthly_income
    })

    debt_breakdown = calculate_total_debt_obligations.invoke({
        "debts": debts,
        "proposed_payment": proposed_payment
    })

    system_prompt = f"""
You are a Senior Income Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

Your task is to analyze the borrower's income and employment profile and provide a detailed assessment.

ANALYSIS FRAMEWORK:
1. Employment Stability - Review job history and tenure
2. Income Verification - Validate income sources
3. DTI Calculation - Use provided calculation (DO NOT recalculate)
4. Payment Capacity - Assess affordability
5. Risk Assessment - Identify income risks
6. Recommendations - Provide conditions if needed

Be thorough, objective, and policy-compliant. Support conclusions with data.
IMPORTANT: Use the EXACT DTI calculation and Housing Ratio provided below. Do not recalculate.
"""

    user_prompt = f"""
Analyze the income profile for case {app_data.get('case_id')}:

EMPLOYMENT DATA:
- Employment Type: {app_data.get('employment', {}).get('type')}
- Employer: {app_data.get('employment', {}).get('employer')}
- Position: {app_data.get('employment', {}).get('position')}
- Years at Job: {app_data.get('employment', {}).get('years')}
- Monthly Income: ${monthly_income:,.2f}
- Income stability notes: {app_data.get('employment', {}).get('notes', 'N/A')}

LOAN & DEBT OBLIGATIONS:
- Proposed Monthly Payment: ${proposed_payment:,.2f}
{debt_breakdown}

CALCULATED DTI (ACCURATE - DO NOT RECALCULATE):
{dti_result}

CALCULATED HOUSING RATIO (ACCURATE - DO NOT RECALCULATE):
{housing_ratio_result}

Provide your detailed income analysis based on the ACCURATE calculations above.
"""

    try:
        llm = get_llm_instance("openai")  
        
        response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
        
        analysis = response.content
        bias_flags = detect_bias_signals(analysis, app_data)
        
        return {
                **state,
                "income_analysis": analysis,
                "bias_flags": state.get("bias_flags", []) + bias_flags,
                "reasoning_chain": state.get("reasoning_chain", []) + [
                    f"Income Analyst: Completed income analysis with DTI calculation"
                ]
            }
    except Exception as e:
        return {
            **state,
            "income_analysis": (
                f"Income analysis could not be completed due to an error: {str(e)}. "
                "Please ensure all income data is complete and retry."
            ),
            "reasoning_chain": state.get("reasoning_chain", []) + [
                "Income Analyst: Encountered an error during analysis"
            ]
        }