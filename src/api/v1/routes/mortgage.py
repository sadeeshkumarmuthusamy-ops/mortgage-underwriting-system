import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.graph.workflow import create_workflow
from src.rag.chunk_dataload import load_policy_store
from src.services.PayloadValidationService import PayloadValidationService

logger = logging.getLogger(__name__)
GRAPH = create_workflow()

router = APIRouter(prefix="/mortgage", tags=["Chat & Agents"])
service = PayloadValidationService()


@router.post("/validate", summary="Validate mortgage documents and provide insights.")
async def stream_chat_response(payload: dict):
    """Accepts mortgage validation requests and provides insights."""
    try:
        is_valid, errors = service.validate_payload(payload)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": errors},
            )

        return {"message": "Mortgage documents validated successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Mortgage validation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"errors": [f"Validation failed: {str(exc)}"]},
        ) from exc


@router.post("/ragload", summary="Load RAG data for mortgage underwriting.")
async def load_rag_data(payload: str):
    """Accepts requests to load RAG data for mortgage underwriting."""
    try:
        response = load_policy_store(payload)
    except Exception as exc:
        logger.exception("RAG policy load failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": [str(exc)]},
        ) from exc

    if response == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": ["No documents were loaded from the provided URL."]},
        )
    return {"message": "documents in the url loaded to vector store", "chunks": response}


@router.post("/mortgageanalysis", summary="Run the underwriting graph for the mortgage application.")
async def credit_analyst(payload: dict | str):
    """Accepts a mortgage application payload and runs it through the underwriting graph."""
    try:
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

        is_valid, errors = service.validate_payload(payload)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": errors},
            )

        test_case_id = payload.get("case_id", f"case_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        config = {"configurable": {"thread_id": test_case_id}}

        inputs = {
            "case_id": test_case_id,
            "applicant_data": payload,
        }

        for event in GRAPH.stream(inputs, config):
            for node_name, node_output in event.items():
                logger.info("Node: %s, Output: %s", node_name, node_output)

        final_state = GRAPH.get_state(config)
        return {"message": final_state}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Mortgage graph execution failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"errors": [f"Mortgage analysis failed: {str(exc)}"]},
        ) from exc