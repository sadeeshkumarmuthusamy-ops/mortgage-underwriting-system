from fastapi import APIRouter, HTTPException, status

from rag.chunk_dataload import load_policy_store
from src.services.PayloadValidationService import PayloadValidationService

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