# Fix End-to-End: Email Triage OpenEnv Project

**Date:** 2026-04-12
**Approach:** B (Fix + Harden)

## Problem

The project has 5 issues preventing end-to-end operation:

1. `requirements.txt` requires `openenv-core>=0.2.0` but only `0.1.0` exists on PyPI — Docker build fails
2. `openai` package missing from `requirements.txt` — inference.py can't import it in Docker
3. `HF_TOKEN` not validated — inference.py crashes with cryptic OpenAI SDK error when token is empty/missing
4. `openenv` CLI doesn't exist in `openenv-core==0.1.0` — validate script step 3 always fails
5. No developer documentation for required env vars or how to run locally

## What Works

- FastAPI server starts and all endpoints (`/reset`, `/step`, `/state`, `/`) return correct responses
- Environment scoring logic is correct (0.05 base + 0.35 category + 0.30 priority + 0.25 reply = 0.95 max)
- Dockerfile structure is sound (just the pip install fails due to bad version pin)

## Changes

### 1. Dependency Fixes (`requirements.txt`)

- `openenv-core>=0.2.0` -> `openenv-core==0.1.0`
- Add `openai>=1.0.0`

No Dockerfile changes needed — it already installs from requirements.txt.

### 2. Inference Client Hardening (`inference.py`)

- Validate `HF_TOKEN` at startup with clear error message and exit
- Wrap LLM API call in try/except — catch auth, rate limit, timeout, and connection errors
- Add JSON parse fallback — catch malformed LLM responses and log which task failed
- Keep sync OpenAI client (async switch is out of scope; sequential 3-task loop is fine)

### 3. Developer Experience

- **`.env.example`** — new file documenting `HF_TOKEN`, `MODEL_NAME`, `API_BASE_URL`
- **`run.sh`** — launcher with `./run.sh server` and `./run.sh infer` commands, includes env var check
- **`validate-submission.sh`** — patch step 3 to warn and skip when `openenv` CLI isn't installed instead of hard-failing

## Out of Scope

- Async OpenAI client migration
- Session isolation / concurrent agent support
- CORS middleware
- Tests
- Production logging infrastructure
