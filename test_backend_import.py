import sys
import os

# Set working path to backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "backend"))

try:
    from src.main import app
    print(f"[PASS] FastAPI app imported successfully. Routes: {len(app.routes)}")
except ImportError as e:
    print(f"[FAIL] ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Exception during import: {type(e).__name__}: {e}")
    sys.exit(1)
