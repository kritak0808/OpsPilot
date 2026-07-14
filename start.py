#!/usr/bin/env python3
"""
OpsPilot AI — Start Script (Windows / cross-platform)
Validates environment and starts all services in sequence.
Run from the project root: python start.py
"""
import subprocess
import sys
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "apps", "backend")
AI_DIR = os.path.join(ROOT, "apps", "ai-orchestrator")


def run(cmd, cwd=None, check=True):
    print(f"  ▶ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=False)
    if check and result.returncode != 0:
        print(f"  ✗ Command failed (exit {result.returncode})")
        sys.exit(result.returncode)
    return result


def main():
    print("\n" + "="*60)
    print("  OpsPilot AI — Local Startup")
    print("="*60)

    # 1. Check .env
    env_file = os.path.join(BACKEND_DIR, ".env")
    if not os.path.exists(env_file):
        print("\n[!] .env not found. Copying .env.example → .env")
        import shutil
        shutil.copy(os.path.join(BACKEND_DIR, ".env.example"), env_file)
        print("    ✓ .env created. Review and update DATABASE_URL / REDIS_URL.")

    # 2. Start infrastructure
    print("\n[1/5] Starting PostgreSQL & Redis via Docker Compose...")
    run(["docker", "compose", "up", "-d", "postgres", "redis"])
    print("      Waiting 5s for services to become healthy...")
    time.sleep(5)

    # 3. Run migrations
    print("\n[2/5] Running Alembic database migrations...")
    run(["python", "-m", "alembic", "-c", "src/database/alembic.ini", "upgrade", "head"], cwd=BACKEND_DIR)

    # 4. Run seed
    print("\n[3/5] Running database seed script...")
    run(["python", "src/database/seed.py"], cwd=BACKEND_DIR)

    # 5. Info
    print("\n[4/5] Starting backend services (open separate terminals):")
    print()
    print("  Terminal 1 — FastAPI Backend:")
    print("    cd apps/backend")
    print("    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("  Terminal 2 — AI Orchestrator:")
    print("    cd apps/ai-orchestrator")
    print("    uvicorn src.main:app --reload --host 0.0.0.0 --port 8001")
    print()
    print("  Terminal 3 — Celery Worker:")
    print("    cd apps/backend")
    print("    celery -A src.workers.celery_app.celery_app worker --loglevel=info")
    print()
    print("  Terminal 4 — Next.js Frontend:")
    print("    pnpm --filter frontend dev")
    print()

    print("[5/5] Service URLs:")
    print()
    print("  Frontend:          http://localhost:3000")
    print("  Backend API:       http://localhost:8000")
    print("  Swagger UI:        http://localhost:8000/docs")
    print("  ReDoc:             http://localhost:8000/redoc")
    print("  AI Service:        http://localhost:8001")
    print("  AI Swagger:        http://localhost:8001/docs")
    print("  Health (Backend):  http://localhost:8000/health")
    print("  Health (AI):       http://localhost:8001/health")
    print()
    print("="*60)
    print("  ✓ Infrastructure started. Launch service terminals above.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
