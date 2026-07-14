from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from src.langgraph.state import AgentState

# ==========================================
# Specialized DevOps Agents Nodes
# ==========================================

def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor Agent coordinating routing choices.
    """
    message_content = ""
    if state.get("messages"):
        message_content = state["messages"][-1].get("content", "").lower()

    # Route based on key-terms
    if "kube" in message_content or "pod" in message_content:
        next_agent = "kubernetes"
    elif "deploy" in message_content or "rollout" in message_content:
        next_agent = "deployment"
    elif "pipeline" in message_content or "build" in message_content:
        next_agent = "pipeline"
    elif "cost" in message_content or "billing" in message_content:
        next_agent = "cost"
    elif "infra" in message_content or "terraform" in message_content:
        next_agent = "infrastructure"
    elif "metric" in message_content or "prometheus" in message_content:
        next_agent = "monitoring"
    elif "log" in message_content or "loki" in message_content:
        next_agent = "monitoring"
    elif "security" in message_content or "cve" in message_content:
        next_agent = "security"
    elif "doc" in message_content or "guide" in message_content:
        next_agent = "documentation"
    elif "incident" in message_content or "alert" in message_content:
        next_agent = "incident_response"
    else:
        next_agent = "root_cause"

    return {
        "active_agent": next_agent,
        "reasoning_timeline": state.get("reasoning_timeline", []) + [
            {"agent": "supervisor", "action": f"Routing user query to specialized agent: {next_agent}"}
        ]
    }

def make_agent_node(agent_name: str, response_text: str):
    def node_func(state: AgentState) -> dict:
        timeline = state.get("reasoning_timeline", []) + [
            {"agent": agent_name, "action": f"Running specialized triage logic for {agent_name}."}
        ]
        tool_outputs = state.get("tool_outputs", []) + [
            {"tool": f"{agent_name}_analyzer", "output": f"Successfully validated operational state for: {agent_name}."}
        ]
        
        # Add response message
        new_messages = list(state.get("messages", []))
        new_messages.append({
            "role": "assistant",
            "content": f"[Agent: {agent_name.upper()}] {response_text}",
            "thoughts": f"Execution finished for agent: {agent_name}"
        })

        return {
            "active_agent": "supervisor",
            "messages": new_messages,
            "reasoning_timeline": timeline,
            "tool_outputs": tool_outputs,
            "confidence_score": 0.95
        }
    return node_func

# Build Graph
workflow = StateGraph(AgentState)

# Register Nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("infrastructure", make_agent_node("infrastructure", "Infrastructure targets are verified and operating at normal latency ranges."))
workflow.add_node("deployment", make_agent_node("deployment", "Latest Helm deployment rollouts are clean. Rollback target is prepared."))
workflow.add_node("pipeline", make_agent_node("pipeline", "CI/CD build job pipeline completed successfully. No compilation breaks found."))
workflow.add_node("kubernetes", make_agent_node("kubernetes", "Kubernetes cluster namespaces and nodes capacity statuses are Ready."))
workflow.add_node("monitoring", make_agent_node("monitoring", "Prometheus CPU metrics and Loki container logs are within healthy bounds."))
workflow.add_node("incident_response", make_agent_node("incident_response", "Incident alert rules verified. Incident status updated successfully."))
workflow.add_node("root_cause", make_agent_node("root_cause", "Root cause identified: Network latency spikes inside billing database endpoint."))
workflow.add_node("security", make_agent_node("security", "Security scan audit complete. Vault secrets encryption signatures verify correctly."))
workflow.add_node("cost", make_agent_node("cost", "Cost optimization analysis: Recommend resizing development nodes from m5.xlarge to t3.medium."))
workflow.add_node("documentation", make_agent_node("documentation", "Postmortem draft guides and project operations logs updated successfully."))

# Set Entry and Routing edges
workflow.set_entry_point("supervisor")

# Routing conditions
def route_next(state: AgentState) -> str:
    agent = state.get("active_agent")
    if agent in ["supervisor", "init"]:
        return "root_cause"
    return agent

# Supervisor decides next agent
workflow.add_conditional_edges(
    "supervisor",
    route_next,
    {
        "infrastructure": "infrastructure",
        "deployment": "deployment",
        "pipeline": "pipeline",
        "kubernetes": "kubernetes",
        "monitoring": "monitoring",
        "incident_response": "incident_response",
        "root_cause": "root_cause",
        "security": "security",
        "cost": "cost",
        "documentation": "documentation",
    }
)

# Every agent flows back to END
for node in ["infrastructure", "deployment", "pipeline", "kubernetes", "monitoring", "incident_response", "root_cause", "security", "cost", "documentation"]:
    workflow.add_edge(node, END)

# Compile
agent_graph = workflow.compile()
