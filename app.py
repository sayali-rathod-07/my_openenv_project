from fastapi import FastAPI, HTTPException
from src.environment import EmailTriageEnv
from src.models import Action, EnvResponse, Observation
import uvicorn

app = FastAPI(title="OpenEnv Email Triage")

# Global environment instance
env = EmailTriageEnv()

@app.post("/reset", response_model=Observation)
async def reset():
    return await env.reset()

@app.post("/step", response_model=EnvResponse)
async def step(action: Action):
    try:
        return await env.step(action)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def state():
    return await env.state()

@app.get("/")
async def root():
    return {"status": "live", "environment": "email-triage-v1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)