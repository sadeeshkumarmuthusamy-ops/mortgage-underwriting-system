import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.graph.workflow import create_workflow
from src.rag.chunk_dataload import load_policy_store
from src.services.PayloadValidationService import PayloadValidationService

GRAPH = create_workflow()

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

@router.post("/creditanalyst", summary="Run the underwriting graph for the mortgage application.")
async def credit_analyst(payload: dict | str):
    """Accepts a mortgage application payload and runs it through the underwriting graph."""

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": [f"Invalid JSON payload: {exc.msg}"]},
            ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": ["Payload must be a JSON object."]},
        )

    state = {
        "case_id": payload.get("case_id", "MTG-2025-001"),
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
        "timestamp": datetime.now().isoformat(),
    }

    config = {"configurable": {"thread_id": "test_case_1"}}
    inputs = {
        "case_id": "MTG-2025-001",
        "applicant_data": payload,
        }
    result = "";
    for event in GRAPH.stream(inputs, config):
        for node_name, node_output in event.items():
            print(f"Node: {node_name}")
    final_state = GRAPH.get_state(config)

    return {
        "message": final_state
    }