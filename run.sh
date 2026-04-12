#!/usr/bin/env bash
set -euo pipefail

# Load .env if present
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

case "${1:-help}" in
    server)
        echo "Starting FastAPI server on port 7860..."
        python3 -m server.app
        ;;
    infer)
        if [ -z "${HF_TOKEN:-}" ]; then
            echo "ERROR: HF_TOKEN is not set."
            echo "  Copy .env.example to .env and fill in your token:"
            echo "  cp .env.example .env"
            exit 1
        fi
        echo "Running inference against http://0.0.0.0:7860 ..."
        python3 inference.py
        ;;
    *)
        echo "Usage: ./run.sh <command>"
        echo ""
        echo "Commands:"
        echo "  server  Start the FastAPI environment server"
        echo "  infer   Run the LLM inference agent"
        ;;
esac
