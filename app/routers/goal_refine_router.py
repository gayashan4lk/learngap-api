

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.goal_refine_models import GoalRefineRequest
from app.models.task_models import TaskResponse
from app.services.goal_refine_service import GoalRefineService

router = APIRouter(
    prefix="/goal-refine",
    tags=["goal-refine"],
)

@router.post("/task", response_model=TaskResponse)
async def create_task(request: GoalRefineRequest, background_tasks: BackgroundTasks):
    task_id = GoalRefineService.create_task()
    background_tasks.add_task(GoalRefineService.process_task, task_id, request)
    return GoalRefineService.get_task_status(task_id)

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    try:
        task = GoalRefineService.get_task_status(task_id)
        return task
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")