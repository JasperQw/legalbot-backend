# LegalBot API Backend

LegalBot API is a Multi-agent AI backend service designed for detecting red flags in tenancy agreements, simplifying legalese, and providing AI-driven legal assistance. This project is built using Python, FastAPI, Google Cloud Platform (Firestore, Cloud Storage, Pub/Sub, Vision), and Google GenAI (Vertex AI).

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Project Architecture & Modules](#project-architecture--modules)

---

## Prerequisites

- **Python 3.10+** (or compatible Python version)
- **Google Cloud Platform (GCP)** Account with necessary APIs enabled:
  - Vertex AI API (for Gemini models)
  - Cloud Firestore API
  - Cloud Storage API
  - Cloud Pub/Sub API
  - Cloud Vision API
- **Service Account Key**: A JSON credentials file associated with a Google Cloud Service Account that has the required permissions.

---

## Setup & Installation

### 1. Clone the repository and navigate to the project directory
```bash
cd legalbot-backend
```

### 2. Set up a virtual environment (Recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# On Windows use: .venv\Scripts\activate
```

### 3. Install dependencies
Install all the required Python packages defined in the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory (alongside `requirements.txt` and `README.md`) to define the necessary Google Cloud parameters. 

**Example `.env` structure:**
```env
GCP_PROJECT_ID="your-gcp-project-id"
GCP_LOCATION="asia-southeast1"
```
*(Replace the values with your actual GCP Project ID and preferred Google Cloud region).*

### 5. Configure Google Service Account Credentials (`serviceAccountKey.json`)
You must download your Google Cloud **Service Account Key** (in JSON format) from the GCP console.
1. Place the JSON file directly in the root directory of the project.
2. Ensure you rename the file exactly to: `serviceAccountKey.json`

The backend reads this file locally (via `./serviceAccountKey.json`) to authenticate services such as Firestore and the Vertex AI/Gemini clients.

---

## Running the Application

The FastAPI application uses `uvicorn` as its ASGI web server. 

To start the local development server, run the following command from the root directory:
```bash
uvicorn app.main:app --reload
```
or 
```bash
fastapi dev app/main.py
```

The application will be accessible at:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **Alternative Redoc Docs**: `http://127.0.0.1:8000/redoc`

---

## Project Architecture & Modules

The codebase is structured into two main directories: `app/` and `common/`. It follows a clean layering pattern separating routing, business logic, and database access.

### `app/` - Core Application
This directory contains the primary functionality of the FastAPI server.

- **`main.py`**: The main entry point. Initializes the FastAPI instance, attaches CORS and request-validation middlewares, and mounts the routers from the controllers.
- **`controllers/`** (Routers): Defines the API endpoints (Routes). They take incoming REST or HTTP requests and map them directly into service layers.
  - `agreement_analysis_controller.py`
  - `agreement_generation_controller.py`
  - `legal_assistant_controller.py`
- **`services/`** (Business Logic): Represents the core logic of the application. It acts as a bridge between the controllers and repositories or external tools.
  - Handles tasks like interacting with Gemini (Vertex AI), performing agreement analysis, parsing documents, handling GCP Cloud Storage uploads, and publishing messages.
  - E.g., `agreement_analysis_service.py`, `gemini_query_service.py`, `pubsub_service.py`, `gcs_service.py`, etc.
- **`repositories/`** (Data Access Layer): Abstracted functions for database operations. Interacts directly with Google Cloud Firestore for persisting and retrieving entities.
  - E.g., `agreement_repository.py`, `consultation_repository.py`, `created_agreement_repository.py`.

### `common/` - Shared Utilities & Configurations
This directory acts as a shared library for use across different services and parts of the application.

- **Cloud Platform Clients**: Singleton and builder modules that initialize connections to Google Cloud services using the `serviceAccountKey.json` file.
  - `firestore.py`, `gcs.py`, `gemini.py`, `pubsub.py`.
- **`schemas.py`**: Pydantic models. Contains the validation schemas for Request payloads and Response structures.
- **`prompts/`**: A subdirectory dedicated to holding custom instructions and templates for querying the Gemini Large Language Model.
