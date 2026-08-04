from fastapi import APIRouter, HTTPException, status

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