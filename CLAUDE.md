# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo shape

This repo contains **three independent applications** that are not built or deployed together. Changes in one rarely require changes in the others — check which app you're actually in before assuming shared code.

- `backend/` — FastAPI API (auth, S3 document upload, LLM-based ATS scoring). This is what `frontend/` talks to.
- `frontend/` — Next.js 16 app (App Router) that consumes `backend/`.
- `streamlit_app/` — standalone Streamlit app with its **own**, separate ATS scoring implementation (rule-based scorer + its own LLM prompt engine). It does not call `backend/` and does not share code with it. Treat it as a second, parallel product, not a client of the FastAPI backend.

## Commands

### backend (FastAPI, Python 3.12, `uv`)

```bash
cd backend
uv sync                                    # installs from pyproject.toml/uv.lock
uv run uvicorn main:app --reload --port 8000
```

`pyproject.toml`/`uv.lock` are missing several packages the code actually imports (`pdfplumber`, `python-docx`, `torch`, `transformers`, `accelerate`, `bitsandbytes`, `psycopg2`, `email-validator`, etc.). `requirements.txt` is the real/complete dependency list — if `uv run` fails on a missing import, install the rest with `uv pip install -r requirements.txt` (or just use `pip install -r requirements.txt` in a venv).

No test suite exists for the backend.

### frontend (Next.js 16, React 19)

```bash
cd frontend
pnpm install    # pnpm-lock.yaml is present; a stray yarn.lock also exists — prefer pnpm
pnpm dev        # http://localhost:3000
pnpm build
pnpm lint
```

Set `NEXT_PUBLIC_API_URL` to point at the backend (defaults to `http://localhost:8000`, see `lib/api.ts`).

### streamlit_app (Python 3.11+, `uv`)

```bash
cd streamlit_app
uv sync
uv run streamlit run app.py     # http://localhost:8501
```

Requires `python -m spacy download en_core_web_sm` for the NLP path. `HUGGING_FACE_API` env var is needed for the LLM (Llama) features; `POSTGRES_URI` for saving extracted profiles.

## Architecture

### backend

Feature-package layout: `auth/`, `upload/`, `ats_score/`, each with `routes.py` + `schemas.py` (+ `utils.py`). Shared pieces live at the package root: `database.py` (SQLAlchemy engine/session, `DATABASE_URL` env, `Base`), `models.py` (`User`, `Document`), `exceptions.py` (custom `HTTPException` subclasses used instead of raising `HTTPException` inline in most routes — follow this pattern for new user/auth/ATS errors).

- **auth**: JWT access+refresh tokens (`auth/utils.py`). Passwords are SHA-256 pre-hashed before bcrypt (`_prepare_password`) specifically to dodge bcrypt's 72-byte input limit — don't "simplify" this away. `SECRET_KEY`/`ALGORITHM`/token TTLs come from env vars with insecure defaults; real deployments must override `SECRET_KEY`.
- **upload**: `upload/s3_service.py` is a singleton (`s3_service`) instantiated at import time and raises immediately if `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`S3_BUCKET_NAME` aren't set — importing this module without S3 env configured will crash the app at startup. Validates extension + content-type + 10MB size cap before upload; documents are tracked in Postgres (`Document` model) with the S3 key, and presigned URLs are generated on read.
- **ats_score**: `ats_score/llm.py` lazily loads `meta-llama/Llama-3.2-3B-Instruct` via `transformers.pipeline` (gated HF model, needs `HUGGING_FACE_API`) and picks device (cuda/mps/cpu) at runtime. `ats_score/utils.py` builds one of two prompts depending on `mode` (`resume_ats` = extract personal info/skills; `resume_vs_jd` = score against a job description) and then has to recover JSON from the raw model output via a hand-rolled brace-matching parser (`extract_json`/`fix_json_str`) since the LLM doesn't reliably emit clean JSON — expect this parsing step to be fragile and a common source of bugs when changing prompts.

### frontend

Two different patterns coexist for calling the backend — know which one a given feature uses before adding to it:

1. **`lib/api.ts`** — a plain `ApiClient` using `fetch` and `NEXT_PUBLIC_API_URL`. Used by the resume-analysis flow (`ats_score/analyze`).
2. **`frontend/workflow/<feature>/<action>/`** — a controller/gateway/types split (`controller.ts` = business logic, `api_gateway.ts` = the actual `axios` call, `*.types.ts`) imported via the `@/workflow/...` path alias. Used by auth (e.g. `workflow/auth/login/`). Note `api_gateway.ts` hardcodes `baseURL: "http://localhost:8000"` rather than reading `NEXT_PUBLIC_API_URL` — inconsistent with `lib/api.ts`.

UI components under `components/ui/` are shadcn/Radix primitives; `components.json` configures shadcn generation. App routes: `app/login`, `app/signup`, `app/dashboard`.

### streamlit_app

Two scoring engines live side by side here too:

- `utils/ats_scoring.py` — deterministic, weighted rule-based scorer (weights documented in `streamlit_app/README.md`: keyword match 40%, density 15%, personal info 15%, skills 10%, experience 10%, education 5%, formatting 5%).
- `utils/ats_engine.py` + `utils/llama_model.py` — a separate LLM-driven engine (see `ATS_ENGINE_GUIDE.md` for its modes/JSON schemas), independent from `ats_scoring.py` and from `backend/ats_score`.

`utils/postgres_client.py` persists LLM-extracted profiles to `POSTGRES_URI`, unrelated to `backend`'s SQLAlchemy/Postgres setup. `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` is set in `llama_model.py` to avoid MPS OOMs on Apple Silicon — keep this if touching model loading on Mac.
