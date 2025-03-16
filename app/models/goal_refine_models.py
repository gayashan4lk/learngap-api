from pydantic import BaseModel

class GoalRefineRequest(BaseModel):
    description: str