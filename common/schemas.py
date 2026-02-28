from pydantic import BaseModel, Field
from enum import Enum

class Status(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class GenerateAgreementStatus(str, Enum):
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    AUDIT = "AUDIT"
    VERIFIED = "VERIFIED"
    FAILED = "FAIELD"

class AgreementWriteTaskType(str, Enum):
    CREATE = "CREATE"
    REVISE = "REVISE"

class SendMessageRequest(BaseModel):
    """Request to send a message to the assistant."""
    text: str = Field(..., description="Message to send to the assistant")

class CreateNewAgreementRequest(BaseModel):
    """Request to create a new agreement."""
    name: str = Field(..., description="Name of the agreement")
    address: str = Field(..., description="Property address")
    start_date: str = Field(..., description="Start date of the agreement")
    duration: int = Field(..., description="Duration of the agreement in months")
    rent: float = Field(..., description="Monthly rent amount")
    special_clauses: str | None = Field(None, description="Optional special clauses to include")