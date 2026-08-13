# @title 6.⚖️ Decision Agent Implementation

from langchain.messages import HumanMessage, SystemMessage

from src.graph.state.UnderwritingState import UnderwritingState
from src.languagemodels.llmprovider import get_llm_instance


def decision_agent_node(state: UnderwritingState) -> UnderwritingState:
    """
    Synthesizes all findings into a final decision and credit memo.

    Determines:
    - Final decision (APPROVED, DENIED, CONDITIONAL_APPROVAL)
    - Risk score (0-100)
    - Conditions if conditional approval
    - Generates audit-ready credit memo
    """


    system_prompt = """
You are the Senior Decision Agent, the final authority in mortgage underwriting.

Your task is to:
1. Synthesize all analyses (Credit, Income, Asset, Collateral, Critic Review).
2. Assign an overall RISK_SCORE (0-100, 0=lowest risk, 100=highest risk).
3. Make a final DECISION (APPROVED, DENIED, CONDITIONAL_APPROVAL).
4. If CONDITIONAL, specify clear conditions.
5. If DENIED, provide specific, policy-backed reasons for the denial.
6. Generate a comprehensive CREDIT_MEMO documenting your rationale and decision.

Consider all compliance alerts (bias flags, policy violations). If bias flags are present, acknowledge them but ensure your decision is based purely on financial and policy criteria. If the application is high risk (e.g., risk_score > 60), or has bias flags, set human_review_required to True.

Structure your response with 'RISK_SCORE:', 'DECISION:', and 'CREDIT_MEMO:' tags.
"""

    user_prompt = f"""
Make final underwriting decision for case {state.get('case_id')}:

CREDIT ANALYSIS SUMMARY:
{state.get('credit_analysis', 'N/A')[:500]}...

INCOME ANALYSIS SUMMARY:
{state.get('income_analysis', 'N/A')[:500]}...

ASSET ANALYSIS SUMMARY:
{state.get('asset_analysis', 'N/A')[:500]}...

COLLATERAL ANALYSIS SUMMARY:
{state.get('collateral_analysis', 'N/A')[:500]}...

CRITIC REVIEW:
{state.get('critic_review', 'N/A')[:500]}...

COMPLIANCE ALERTS:
- Bias Flags: {len(state.get('bias_flags', []))}
- Policy Violations: {len(state.get('policy_violations', []))}

Provide:
1. RISK_SCORE: (number 0-100)
2. DECISION: (APPROVED/DENIED/CONDITIONAL_APPROVAL)
3. CREDIT_MEMO: (comprehensive decision documentation)
"""

    # Generate decision using llm directly
    llm = get_llm_instance("openai")  # Assuming this function returns an LLM instance
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # Parse response for risk score and decision
    content = response.content

    # Extract risk score
    risk_score = 50  # default
    if "RISK_SCORE:" in content:
        import re
        match = re.search(r'RISK_SCORE:\s*(\d+)', content)
        if match:
            risk_score = int(match.group(1))

    # Extract decision
    decision = "CONDITIONAL_APPROVAL"  # default
    if "APPROVED" in content and "CONDITIONAL" not in content:
        decision = "APPROVED"
    elif "DENIED" in content:
        decision = "DENIED"
    elif "CONDITIONAL_APPROVAL" in content or "CONDITIONAL APPROVAL" in content:
        decision = "CONDITIONAL_APPROVAL"

    # Determine if human review needed (high risk or bias flags)
    human_review_required = (
        risk_score >= 65 or
        len(state.get('bias_flags', [])) > 0 or
        decision == "DENIED"
    )

    return {
        **state,
        "decision_memo": content,
        "risk_score": risk_score,
        "final_decision": decision,
        "human_review_required": human_review_required,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Decision Agent: Final decision {decision} with risk score {risk_score}"
        ]
    }
