from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ChatPrompt(BaseModel):
    prompt: str = Field(min_length=1)
    conversation_id: Optional[UUID] = None

class DiagnosePrompt(BaseModel):
    incident_id: UUID

class AIConversationResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class AIMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    thoughts: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AIRecommendationResponse(BaseModel):
    category: str
    impact: str
    confidence: float
    description: str
    actions: List[str]
