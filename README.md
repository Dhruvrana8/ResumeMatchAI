# ResumeMatchAI — ATS Resume Scanner

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-Python%203.12-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-16-black.svg" alt="Next.js">
  <img src="https://img.shields.io/badge/React-19-blue.svg" alt="React">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🎯 Overview

**ResumeMatchAI** analyzes resumes against job descriptions to provide ATS compatibility scores and actionable improvement recommendations, powered by an LLM-based scoring engine.

### ✨ Key Features

- **🔐 Authentication**: JWT access + refresh token auth
- **📄 Resume Upload**: S3-backed document upload with validation (extension, content-type, 10MB cap)
- **🤖 AI-Powered ATS Scoring**: Meta Llama 3.2-3B-Instruct model scores resume vs. job description
- **🌐 Modern Web UI**: Next.js 16 (App Router) frontend

## 🏗️ Repo Structure

This repo contains **two independent applications**:

```
ResumeMatchAI/
├── backend/     # FastAPI API — auth, S3 upload, LLM-based ATS scoring
└── frontend/    # Next.js 16 app that consumes backend/
```

## 🚀 Quick Start

### backend (FastAPI, Python 3.12, `uv`)

```bash
cd backend
uv sync                                    # installs from pyproject.toml/uv.lock
uv run uvicorn main:app --reload --port 8000
```

`pyproject.toml`/`uv.lock` are missing several packages the code actually imports (`pdfplumber`, `python-docx`, `torch`, `transformers`, `accelerate`, `bitsandbytes`, `psycopg2`, `email-validator`, etc.). `requirements.txt` is the real/complete dependency list — if `uv run` fails on a missing import, install the rest with `uv pip install -r requirements.txt` (or `pip install -r requirements.txt` in a venv).

Env vars: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`S3_BUCKET_NAME`, `HUGGING_FACE_API` (for the ATS scoring model).

### frontend (Next.js 16, React 19)

```bash
cd frontend
pnpm install
pnpm dev        # http://localhost:3000
```

Set `NEXT_PUBLIC_API_URL` to point at the backend (defaults to `http://localhost:8000`).

## 📋 How It Works

1. **Sign up / log in** — JWT-based auth.
2. **Upload a resume** — PDF/DOCX, stored in S3, tracked in Postgres.
3. **Analyze against a job description** — `ats_score/analyze` sends the resume + JD to the LLM, which scores the match and returns structured feedback.
4. **View results** — score breakdown and recommendations in the dashboard.

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, AWS S3, Transformers (Meta Llama 3.2-3B-Instruct)
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/Radix UI

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
