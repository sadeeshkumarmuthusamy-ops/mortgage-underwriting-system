from fastapi import APIRouter

router = APIRouter(prefix="/mortgage", tags=["Chat & Agents"])

@router.post("/validate", summary="Validate mortgage documents and provide insights.")
async def stream_chat_response(payload: dict):
    """Accepts mortgage validation requests and provides insights."""
    if not isinstance(payload, dict):
        return {"error": "Payload must be a JSON object."}

    print(f"Received payload: {payload}")
    # Simulate a response (replace with actual mortgage validation logic)
    response = "Mortgage documents validated successfully."
    print(f"Financial Agent response: {response}")
    return {"message": response}