import asyncio
from .models import Observation, Action, EnvResponse

class EmailTriageEnv:
    def __init__(self):
        # Mandatory 3 Tasks (Easy -> Medium -> Hard)
        self.tasks = [
            {
                "id": "easy_1",
                "sender": "no-reply@marketing.com",
                "subject": "HUGE SALE!",
                "body": "Buy now or miss out on these crypto gains!",
                "correct_cat": "spam",
                "correct_pri": "low"
            },
            {
                "id": "med_1",
                "sender": "billing@cloud.com",
                "subject": "Invoice Overdue",
                "body": "Your subscription for account #99 has failed. Please pay $50.",
                "correct_cat": "billing",
                "correct_pri": "high"
            },
            {
                "id": "hard_1",
                "sender": "customer@gmail.com",
                "subject": "Feature Request & Bug",
                "body": "I love the app, but the login button is broken on Safari. Can you add Dark Mode?",
                "correct_cat": "support",
                "correct_pri": "medium"
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
        reward = 0.0
        
        # --- Programmatic Grader Logic ---
        # 1. Check Category (0.4 points)
        if action.category.lower() == current_task["correct_cat"]:
            reward += 0.4
        
        # 2. Check Priority (0.3 points)
        if action.priority.lower() == current_task["correct_pri"]:
            reward += 0.3
            
        # 3. Check Reply Quality (0.3 points)
        # Simple deterministic check: reply must be > 10 chars and mention the sender's domain
        domain = current_task["sender"].split("@")[-1]
        if len(action.reply_draft) > 10 and (domain in action.reply_draft or "Thank you" in action.reply_draft):
            reward += 0.3

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