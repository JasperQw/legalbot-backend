from dotenv import load_dotenv
from google import genai
from google.oauth2 import service_account
import os

load_dotenv()

_client = None
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION")

def get_gemini_client() -> genai.Client:
    global _client

    if _client is None:
        creds = service_account.Credentials.from_service_account_file(
            "./serviceAccountKey.json",
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        _client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location=GCP_LOCATION,
            credentials=creds
        )

    return _client

DEFAULT_MODEL = "gemini-2.5-flash"
