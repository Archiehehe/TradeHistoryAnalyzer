# TradeHistoryAnalyzer

TradeHistoryAnalyzer is a production-oriented trading-behavior audit app. It accepts uploaded transaction history files, reconstructs trading activity, surfaces possible patterns, and produces a plain-English report focused on behavior rather than portfolio advice.

## API Keys Required Before First Run

The app is designed around real integrations from the first implementation. Copy `.env.example` to `.env` and configure the following values before starting the backend.

### Required

- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `DATABASE_URL` or `NEON_DATABASE_URL`
- `SEC_USER_AGENT` formatted like `app-name/version contact-email`

### Optional but supported from day one

- `FMP_API_KEY`
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`
- `R2_PUBLIC_BASE_URL`

### Where each key is used

- `GEMINI_API_KEY`: `backend/app/ai/providers/gemini_client.py` for final report narrative generation.
- `GROQ_API_KEY`: `backend/app/ai/providers/groq_client.py` for transaction classification, theme classification, and fast trade tagging.
- `ALPHA_VANTAGE_API_KEY`: `backend/app/market_data/alpha_vantage.py` for primary historical price series.
- `DATABASE_URL` / `NEON_DATABASE_URL`: `backend/app/db/session.py` for SQLAlchemy engine creation and persistent storage.
- `SEC_USER_AGENT`: reserved for SEC-compliant outbound requests and future filing enrichment hooks.
- `FMP_API_KEY`: `backend/app/market_data/fmp.py` for fallback market-data history.
- `R2_*`: `backend/app/storage/r2.py` for Cloudflare R2-backed raw file storage.

## Project structure

```text
frontend/    SvelteKit app, Tailwind UI, upload/review/report workflow
backend/     FastAPI app, parsers, services, AI router, market-data router, Alembic
```

## Run From Repo Root

Use these PowerShell helpers from the repo root:

```powershell
.\scripts\Start-Backend.ps1
.\scripts\Start-Frontend.ps1
.\scripts\Test-Backend.ps1
.\scripts\Check-Frontend.ps1
.\scripts\Migrate-Database.ps1
.\scripts\Get-IntegrationStatus.ps1
```

Defaults:
- `Start-Backend.ps1` uses `backend\.venv\Scripts\python.exe` if it exists, otherwise it falls back to `python` on `PATH`.
- `Start-Frontend.ps1` sets `PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api` unless you already exported a value.
- `Migrate-Database.ps1` runs `alembic upgrade head` by default. Pass `-Command current`, `-Command history`, or `-Command downgrade` to change behavior.
- `Get-IntegrationStatus.ps1` prints the safe `/api/integrations/status` payload from a running backend.

### One-Time Setup

- Backend: create a virtual environment in `backend/.venv` and install dependencies from `backend/pyproject.toml`.
- Frontend: run `npm install` once inside `frontend/`.

### What The Scripts Map To

- Backend dev server: `uvicorn app.main:app --reload`
- Frontend dev server: `npm run dev`
- Backend tests: `pytest tests`
- Frontend checks: `npm run check`
- Database migrations: `alembic upgrade head`
- Integration status: `GET /api/integrations/status`

## Database Migrations

- Alembic config lives in `backend/alembic.ini`.
- Migration environment lives in `backend/alembic/env.py`.
- The initial schema is `backend/alembic/versions/20260711_0001_initial_schema.py`.

## Testing

Backend tests live under `backend/tests/` and cover:

- column detection
- date parsing
- action normalization
- unknown-row handling
- Seeking Alpha portfolio parsing
- integration status handling
- rule-based report generation without AI
- AI-output schema validation

Run them from the repo root with:

```powershell
.\scripts\Test-Backend.ps1
```

## Production deployment notes

- Frontend target: Vercel using SvelteKit and `@sveltejs/adapter-vercel`.
- Backend target: separate FastAPI deployment with access to Neon Postgres.
- File storage uses the local filesystem in development and can switch to Cloudflare R2 when the `R2_*` variables are present.
- Secret keys stay server-side. The frontend only consumes safe integration status flags from `GET /api/integrations/status`.
