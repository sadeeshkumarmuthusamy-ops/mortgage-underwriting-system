from datetime import datetime
from unittest import result

from fastapi import APIRouter, HTTPException, status

from agents.credit_analyst_node import credit_analyst_node
from rag.chunk_dataload import load_policy_store
from src.services.PayloadValidationService import PayloadValidationService
from src.utils.helper_functions import initialize_application, sanitize_pii_node

router = APIRouter(prefix="/mortgage", tags=["Chat & Agents"])
service = PayloadValidationService()


@router.post("/validate", summary="Validate mortgage documents and provide insights.")
async def stream_chat_response(payload: dict):
    """Accepts mortgage validation requests and provides insights."""
    is_valid, errors = service.validate_payload(payload)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors},
        )

    return {"message": "Mortgage documents validated successfully."}

@router.post("/ragload", summary="Load RAG data for mortgage underwriting.")
async def load_rag_data(payload: str):
    """Accepts requests to load RAG data for mortgage underwriting."""
    try:
        response = load_policy_store(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": [str(e)]},
        )
    if(response == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": ["No documents were loaded from the provided URL."]},
        )
    return {"message": "documents in the url loaded to vector store", "chunks": response}

@router.post("/creditanalyst", summary="Load RAG data for mortgage underwriting.")
async def credit_analyst(payload: str):
    """Accepts requests to load RAG data for mortgage underwriting."""

    # Initialize state ONCE
    initial_inputs = {
        "case_id": "MTG-2025-001",
        "applicant_data": payload,
        "sanitized_data": {},
        "credit_analysis": None,
        "income_analysis": None,
        "asset_analysis": None,
        "collateral_analysis": None,
        "critic_review": None,
        "decision_memo": None,
        "final_decision": None,
        "risk_score": None,
        "next_agent": None,
        "analysis_complete": False,
        "human_review_required": False,
        "human_review_completed": False,
        "human_notes": None,
        "bias_flags": [],
        "policy_violations": [],
        "reasoning_chain": [],
        "timestamp": datetime.now().isoformat()
        }

    TC_01_state_0 = initialize_application(initial_inputs)
    TC_01_state_0 = sanitize_pii_node(TC_01_state_0)

    TC_01_state_1 = credit_analyst_node(TC_01_state_0)

    result = TC_01_state_1
    print(result.get("credit_analysis", "No analysis generated"))

    print("🔍 Reasoning Chain:")
    for step in result.get("reasoning_chain", []):
        print(f"   → {step}")
    return {"message": result.get("credit_analysis", "No analysis generated"), "reasoning_chain": result.get("reasoning_chain", [])}