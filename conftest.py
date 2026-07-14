"""
pytest conftest — adds apps/backend to sys.path so `src.*` imports work
when running pytest from the monorepo root.
"""
import sys
import os

# Ensure the backend src package is importable regardless of working directory
backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
