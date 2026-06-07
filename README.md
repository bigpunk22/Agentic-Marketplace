# Agentic Marketplace — Root Configuration

## Project Structure
```
agentic-marketplace/
├── frontend/          # Next.js 14+ (TypeScript) — App Router
├── backend/           # FastAPI (Python) — Async API
├── e2e/               # Playwright E2E tests
├── infrastructure/    # Docker, K8s, Terraform, Helm
├── docs/              # Architecture, API docs, guides
├── scripts/           # Utility scripts
├── .github/           # CI/CD workflows
└── prd.md             # Product Requirements Document
```

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### Development

```bash
# Start infrastructure services
docker compose up -d postgres redis qdrant

# Backend
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Environment Variables

See `.env.example` files in `frontend/` and `backend/` for required variables.

## Architecture
- **Frontend:** Next.js 14 App Router, React Server Components, Tailwind CSS, Zustand
- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Celery, Socket.IO
- **Database:** PostgreSQL 16, Redis 7, Qdrant (vector)
- **AI:** OpenRouter (multi-model), custom agent orchestration layer
- **Infrastructure:** Docker, Kubernetes, Cloudflare, GitHub Actions

## License
Proprietary — All rights reserved.
