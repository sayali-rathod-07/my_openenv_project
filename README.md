# Email Triage & Automation Environment (OpenEnv)

## Overview
This project implements a real-world **Email Triage** environment using the OpenEnv specification. It simulates an AI agent acting as an automated executive assistant that must process, prioritize, and draft responses to various customer and system emails.

## Real-World Utility (30%)
Unlike "toy" problems, this environment models a genuine business task. It evaluates an agent's ability to:
- Distinguish between urgent billing issues and low-priority spam.
- Understand professional context to provide meaningful reply drafts.
- Handle multi-intent customer support queries.

## Environment Specification
- **Benchmark Name**: `email-triage-env`
- **Framework**: OpenEnv (FastAPI + Pydantic)
- **Tasks**: 3 tasks ranging from Easy (Spam detection) to Hard (Multi-intent support).

### Action Space
The agent must provide a structured response for every email:
- `category`: Classification of the email (e.g., `support`, `billing`, `spam`).
- `priority`: Urgency level (`low`, `medium`, `high`).
- `reply_draft`: A drafted response to the sender.

### Observation Space
The agent receives:
- `sender`: Originating email address.
- `subject`: Header information.
- `body`: Full text of the message.
- `current_folder`: Context of where the mail was found.

## Project Structure
```text
my_openenv_project/
├── openenv.yaml          # Environment metadata
├── requirements.txt      # Dependencies (FastAPI, Pydantic, etc.)
├── Dockerfile            # Container configuration
├── app.py                # FastAPI server exposing the environment
├── inference.py          # AI Agent logic and baseline script
└── src/
    ├── models.py         # Pydantic data schemas
    └── environment.py    # Logic for 3 tasks and programmatic grading
