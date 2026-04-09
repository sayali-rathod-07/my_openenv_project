import os
import asyncio
import httpx
from openai import OpenAI
from src.models import Action

# Environment Variables (Required by OpenEnv)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN")
# For local testing, we point to your running server
ENV_URL = "http://0.0.0.0:7860" 

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def log_start(task: str):
    print(f"[START] task={task} env=email-triage-env model={MODEL_NAME}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list):
    rew_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rew_str}", flush=True)

async def get_agent_action(obs):
    prompt = f"""
    You are an Email Triage Agent. 
    Email from: {obs['sender']}
    Subject: {obs['subject']}
    Body: {obs['body']}

    Respond ONLY with a JSON object in this format:
    {{"category": "spam|billing|support", "priority": "low|medium|high", "reply_draft": "your message here"}}
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    import json
    return json.loads(response.choices[0].message.content)

async def run_inference():
    log_start("email-triage-task")
    
    rewards = []
    steps = 0
    
    async with httpx.AsyncClient() as http_client:
        # 1. Reset
        resp = await http_client.post(f"{ENV_URL}/reset")
        obs = resp.json()
        
        done = False
        while not done: # We have 3 tasks
            steps += 1
            
            # 2. Get AI Decision
            action_data = await get_agent_action(obs)
            
            # 3. Step the environment
            step_resp = await http_client.post(f"{ENV_URL}/step", json=action_data)
            result = step_resp.json()
            
            reward = result['reward']
            done = result['done']
            obs = result['observation']
            
            rewards.append(reward)
            
            # 4. Log Step (mandatory format)
            action_summary = f"{action_data['category']}-{action_data['priority']}"
            log_step(steps, action_summary, reward, done)

        # 5. Final Score
        total_score = sum(rewards) / 3.0 # Max reward is 1.0 per task
        success = total_score >= 0.7
        log_end(success, steps, total_score, rewards)

if __name__ == "__main__":
    asyncio.run(run_inference())