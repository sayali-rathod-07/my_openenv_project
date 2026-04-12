# Fix End-to-End: Email Triage OpenEnv Project

**Date:** 2026-04-12 (revised)
**Approach:** B (Fix + Harden)

## Problem

The project has 7 issues preventing end-to-end operation:

### P0 — Submission Blocker
1. **OpenEnv validation fails: "Not enough tasks with graders"** — the `openenv.yaml` grader config is broken:
   - Task IDs in YAML (`task_1_easy`, `task_2_medium`, `task_3_hard`) don't match environment.py (`task_1_support`, `task_2_billing`, `task_3_spam`)
   - Grader `prompt_template` is a placeholder stub, not a real grading prompt
   - Environment class doesn't follow the OpenEnv Rubric pattern — scoring logic is loose in `step()` instead of a proper `Rubric` subclass with `forward()` method
   - YAML schema is non-standard — missing `spec_version`, using custom fields instead of the official format

### P1 — Build/Runtime Failures
2. `requirements.txt` requires `openenv-core>=0.2.0` but only `0.1.0` exists on PyPI — Docker build fails
3. `openai` package missing from `requirements.txt` — inference.py can't import it in Docker
4. `HF_TOKEN` not validated — inference.py crashes with cryptic OpenAI SDK error when token is empty/missing

### P2 — Developer Experience
5. `openenv` CLI doesn't exist in `openenv-core==0.1.0` — validate script step 3 always fails
6. No developer documentation for required env vars or how to run locally

## What Works

- FastAPI server starts and all endpoints (`/reset`, `/step`, `/state`, `/`) return correct responses
- Environment scoring logic is correct (0.05 base + 0.35 category + 0.30 priority + 0.25 reply = 0.95 max)
- Dockerfile structure is sound (just the pip install fails due to bad version pin)

## Changes

### 0. Grader/Rubric Fix (P0 — Submission Blocker)

**`src/environment.py`:**
- Extract scoring logic from `step()` into a proper `EmailTriageRubric` class with a `forward(action, observation)` method returning 0.0-1.0
- Add `self.rubric = EmailTriageRubric()` attribute to `EmailTriageEnv.__init__()`
- Call `self.rubric(action, obs)` in `step()` instead of inline scoring

**`openenv.yaml`:**
- Align task IDs with environment.py: `task_1_support`, `task_2_billing`, `task_3_spam`
- Change grader type from `"llm"` to `"programmatic"` referencing the Rubric class
- Add `spec_version: 1` and proper metadata fields
- Write real grader descriptions instead of placeholder stubs

### 1. Dependency Fixes (`requirements.txt`)

- `openenv-core>=0.2.0` -> `openenv-core==0.1.0`
- Add `openai>=1.0.0`

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
