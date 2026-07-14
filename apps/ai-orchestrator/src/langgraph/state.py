from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Core graph state properties passed across agents in the orchestrator run.
    All keys are optional (total=False) so that agent nodes can return partial
    state updates without raising KeyError during LangGraph state merging.
    """
    messages: List[Dict[str, Any]]
    active_agent: str
    incident_context: Dict[str, Any]
    active_errors: List[str]
    git_branch: str
    reasoning_timeline: List[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]
    confidence_score: float
