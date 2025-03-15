from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.task_models import TaskResponse
from app.services.goal_refine_service import GoalRefineService
from pydantic import BaseModel

class GoalRefineRequest(BaseModel):
    description: str

router = APIRouter(
    prefix="/goal_refine",
    tags=["goal_refine"],
    responses={404: {"description": "Not found"}},
)
    
@router.post("/", response_model=TaskResponse)
async def create_goal_refine_task(request: GoalRefineRequest, background_tasks: BackgroundTasks):
    task_id = GoalRefineService.create_task(request.description)
    background_tasks.add_task(GoalRefineService.process_task, task_id, request.description)
    return GoalRefineService.get_task_status(task_id)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_goal_refine_task(task_id: str):
    task = GoalRefineService.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
