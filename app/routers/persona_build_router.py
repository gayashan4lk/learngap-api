from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.task_models import TaskResponse
from app.services.persona_build_service import PersonaBuildService
from app.models.user_models import UserPersonaRequest

router = APIRouter(
    prefix="/persona-build",
    tags=["persona-build"],
)
    
@router.post("/task", response_model=TaskResponse)
async def create_task(request: UserPersonaRequest, background_tasks: BackgroundTasks):
    task_id = PersonaBuildService.create_task()
    background_tasks.add_task(PersonaBuildService.process_task, task_id, request)
    return PersonaBuildService.get_task_status(task_id)

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    try:
        task = PersonaBuildService.get_task_status(task_id)
        return task
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")