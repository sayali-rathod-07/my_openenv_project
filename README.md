---
title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Email Triage & Automation

An OpenEnv reinforcement learning environment for training agents to categorize, prioritize, and respond to emails.

## Overview

This project implements an RL environment server (FastAPI) that presents email triage tasks to an agent. The agent must classify each email by category, assign a priority, and draft a reply. A programmatic rubric scores the agent's performance.

**3 tasks** with increasing difficulty:

| Task | Email Type | Correct Category | Correct Priority |
|------|-----------|-----------------|-----------------|
| Easy | Customer support (broken login) | support | high |
| Medium | Billing (overdue invoice) | billing | high |
| Hard | Spam (prize scam) | spam | low |

**Scoring** (per task, max 0.95):
- Category match: +0.35
- Priority match: +0.30
- Reply draft > 10 chars: +0.25
- Base: +0.05

## Prerequisites

- Python 3.10+
- Docker (for deployment)
- A [HuggingFace API token](https://huggingface.co/settings/tokens) (for running inference)

## Setup

```bash
# Clone the repo
git clone https://github.com/sayali-rathod-07/my_openenv_project.git
cd my_openenv_project

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your HF_TOKEN
```

## Usage

### Start the server

```bash
./run.sh server
```

The FastAPI server starts on `http://0.0.0.0:7860`.

### Run inference

In a separate terminal:

```bash
./run.sh infer
```

This runs the LLM-powered agent (Qwen/Qwen2.5-72B-Instruct) through all 3 tasks.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/reset` | Reset environment, returns first email observation |
| POST | `/step` | Submit an action (category, priority, reply_draft), returns reward |
| GET | `/state` | Get current task index and done status |

### Example request

```bash
# Reset
curl -X POST http://localhost:7860/reset

# Step with an action
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"category": "support", "priority": "high", "reply_draft": "We are looking into this."}'
```

## Docker

```bash
# Build
docker build -t email-triage-env .

# Run
docker run -p 7860:7860 email-triage-env
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Yes (for inference) | — | HuggingFace API token |
| `MODEL_NAME` | No | `Qwen/Qwen2.5-72B-Instruct` | LLM model for inference |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM API endpoint |

## Project Structure

```
├── server/app.py          # FastAPI server entry point
├── src/
│   ├── environment.py     # EmailTriageEnv + EmailTriageRubric
│   └── models.py          # Pydantic models (Action, Observation, EnvResponse)
├── inference.py           # LLM-powered inference agent
├── openenv.yaml           # OpenEnv configuration (tasks, graders)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker container config
├── run.sh                 # Launcher script
├── .env.example           # Environment variable template
└── validate-submission.sh # Submission validation script
```

## Validation

```bash
./validate-submission.sh <your-hf-space-url>
```

Checks: HF Space is live, Docker builds, and openenv validates.
