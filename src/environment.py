import asyncio
from .models import Observation, Action, EnvResponse

class EmailTriageEnv:
    def __init__(self):
        # Mandatory 3 Tasks (Easy -> Medium -> Hard)
        self.tasks = [
            {
                "id": "task_1_support",
                "sender": "customer@example.com",
                "subject": "Broken Link",
                "body": "I cannot access the login page. Please help.",
                "correct_cat": "support",
                "correct_pri": "high"
            },
            {
                "id": "task_2_billing",
                "sender": "accounts@example.com",
                "subject": "Invoice #1234",
                "body": "Your payment is overdue by 5 days.",
                "correct_cat": "billing",
                "correct_pri": "high"
            },
            {
                "id": "task_3_spam",
                "sender": "win-free-money@scam.com",
                "subject": "YOU WON!",
                "body": "Click here to claim your $1,000,000 prize now!",
                "correct_cat": "spam",
                "correct_pri": "low"
            }
        ]
        self.current_idx = 0
        self.done = False

    async def reset(self) -> Observation:
        self.current_idx = 0
        self.done = False
        return self._get_obs()

    def _get_obs(self) -> Observation:
        t = self.tasks[self.current_idx]
        return Observation(
            email_id=t["id"],
            sender=t["sender"],
            subject=t["subject"],
            body=t["body"],
            current_folder="Inbox"
        )

    async def step(self, action: Action) -> EnvResponse:
        current_task = self.tasks[self.current_idx]
        
        # --- Programmatic Grader Logic (Fuzzy Scoring) ---
        # Start with a base reward of 0.05 (Strictly > 0)
        reward = 0.05
        
        # 1. Check Category (Add up to 0.35 points)
        if action.category.lower() == current_task["correct_cat"]:
            reward += 0.35
        
        # 2. Check Priority (Add up to 0.30 points)
        if action.priority.lower() == current_task["correct_pri"]:
            reward += 0.30
            
        # 3. Check Reply Quality (Add up to 0.25 points)
        # Max total possible: 0.05 + 0.35 + 0.30 + 0.25 = 0.95 (Strictly < 1)
        if len(action.reply_draft) > 10:
            reward += 0.25

        self.current_idx += 1
        if self.current_idx >= len(self.tasks):
            self.done = True

        obs = self._get_obs() if not self.done else None
        
        return EnvResponse(
            observation=obs,
            reward=round(reward, 2),
            done=self.done,
            info={"task_id": current_task["id"]}
        )

    async def state(self):
        return {"current_task": self.current_idx, "is_done": self.done}

    async def close(self):
        pass