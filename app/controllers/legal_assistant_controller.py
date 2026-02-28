from fastapi import APIRouter
from app.services.legal_assistant_service import get_consultation_history, send_consultation_message
from common.schemas import SendMessageRequest

router = APIRouter(prefix="/api/v1/assistant/consultation", tags=["Legal Assistant"])

@router.get("/history")
async def get_consultation_history_route():
    return await get_consultation_history()

@router.post("/send")
async def send_consultation_message_route(request: SendMessageRequest):
    return await send_consultation_message(request)