from fastapi import FastAPI
from src.langgraph.graph import agent_graph

def create_app() -> FastAPI:
    app = FastAPI(
        title="OpsPilot AI Agent Orchestrator",
        version="1.0.0",
        docs_url="/docs",
    )

    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "healthy", "service": "ai-orchestrator"}

    @app.post("/api/v1/agent/run", tags=["Orchestrator"])
    async def execute_agent_graph(payload: dict):
        # Setup initial graph execution state
        initial_state = {
            "messages": payload.get("messages", []),
            "active_agent": "init",
            "incident_context": payload.get("context", {}),
            "active_errors": [],
            "git_branch": payload.get("branch", "main"),
        }
        
        # Invoke LangGraph state machine runnable
        output = await agent_graph.ainvoke(initial_state)
        return {"state": output}

    return app

app = create_app()
