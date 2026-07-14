import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "ai-orchestrator"))

try:
    from src.langgraph.graph import agent_graph
    print("[PASS] AI Orchestrator LangGraph compiled successfully")
except ImportError as e:
    print(f"[FAIL] ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Exception: {type(e).__name__}: {e}")
    sys.exit(1)
