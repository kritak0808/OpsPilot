from uuid import uuid4
import pytest
from src.models.ai import AIConversation, AIMessage

# ==========================================
# Unit Tests: AI Conversation & Messages
# ==========================================

def test_conversation_model_instantiation() -> None:
    project_id = uuid4()
    conv = AIConversation(
        project_id=project_id,
        title="Production Triage Thread"
    )
    assert conv.title == "Production Triage Thread"
    assert conv.project_id == project_id

def test_message_reasoning_trail() -> None:
    conversation_id = uuid4()
    msg = AIMessage(
        conversation_id=conversation_id,
        role="assistant",
        content="Analyzed Prometheus charts. Scale actions verified.",
        thoughts="Supervisor node routed to DeploymentAgent."
    )
    assert msg.role == "assistant"
    assert "Prometheus" in msg.content
    assert "Supervisor" in msg.thoughts
    assert msg.conversation_id == conversation_id
