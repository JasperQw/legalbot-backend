from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import agreement_analysis_controller, agreement_generation_controller, legal_assistant_controller

app = FastAPI(
    title="LegalBot API",
    description=(
        "Multi-agent AI backend for detecting red flags in tenancy agreements. "
        "Modules 4.0 (Simplify Legalese) and 5.0 (ToS Gotcha Analyzer)."
    ),
    version="0.1.0",
)


@app.middleware("http")
async def normalize_json_body(request: Request, call_next):
    """
    Normalize literal control characters in JSON request bodies.
    Replaces raw newlines/tabs inside JSON strings so that multi-line
    text pasted from Swagger UI or curl doesn't break JSON parsing.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        raw = await request.body()
        if raw:
            # Replace literal control characters with JSON escape sequences
            fixed = (
                raw
                .replace(b"\r\n", b"\\n")
                .replace(b"\r", b"\\n")
                .replace(b"\n", b"\\n")
                .replace(b"\t", b"\\t")
            )
            # Rebuild the request with the cleaned body
            async def receive():
                return {"type": "http.request", "body": fixed, "more_body": False}
            request = Request(request.scope, receive)

    return await call_next(request)


# CORS — allow all origins for hackathon speed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "LegalBot API",
        "version": "0.1.0",
    }


# Mount routers
app.include_router(legal_assistant_controller.router)
app.include_router(agreement_analysis_controller.router)
app.include_router(agreement_generation_controller.router)