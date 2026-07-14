from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class AIConversation(SQLModel, table=True):
    __tablename__ = "ai_conversations"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    title: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["AIMessage"] = Relationship(back_populates="conversation", cascade_delete=True)

class AIMessage(SQLModel, table=True):
    __tablename__ = "ai_messages"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="ai_conversations.id", index=True, ondelete="CASCADE")
    role: str = Field(nullable=False)  # user, assistant, system
    content: str = Field(nullable=False)
    thoughts: Optional[str] = Field(default=None)  # Reasoning chain details
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: AIConversation = Relationship(back_populates="messages")
