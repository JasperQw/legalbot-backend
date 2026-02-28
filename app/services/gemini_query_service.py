from common.gemini import DEFAULT_MODEL, get_gemini_client


client = get_gemini_client()

async def gemini_generate_content(contents, model=DEFAULT_MODEL, temperature=0.1, system_instruction=None):
    return client.models.generate_content(
        model=model,
        config={
            "system_instruction": system_instruction,
            "temperature": temperature,
        },
        contents=contents
    )