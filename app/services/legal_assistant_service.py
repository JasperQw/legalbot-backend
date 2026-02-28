from app.repositories.consultation_repository import create_consultation_message, select_all_consultation_history
from app.services.gemini_query_service import gemini_generate_content
from common.prompts.legal_assistant_prompts import LEGAL_ASSISTANT_PROMPT
from common.schemas import SendMessageRequest

async def get_consultation_history():
    data = await select_all_consultation_history()
    return {
        "items": data
    }

async def send_consultation_message(request: SendMessageRequest):
    await create_consultation_message(request.text, "user")

    history = await select_all_consultation_history()
    formatted_history = [
            {
                "role": item["role"],
                "parts": [{"text": item["text"]}]
            }
            for item in history
        ]
    response = await gemini_generate_content(
        system_instruction=LEGAL_ASSISTANT_PROMPT,
        contents=[
            *formatted_history,
            {
                "role": "user", 
                "parts": [{"text": request.text}]
            }
        ]
    )

    return await create_consultation_message(response.text, "model")
    