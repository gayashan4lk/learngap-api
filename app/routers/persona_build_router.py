from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.user_models import UserVM
from app.models.task_models import TaskResponse, TopicRequest
from app.services.persona_build_service import PersonaBuildService

router = APIRouter(
    prefix="/persona-build",
    tags=["persona-build"],
    responses={404: {"description": "Not found"}},
)
    
@router.post("/task", response_model=TaskResponse)
async def create_task(request: TopicRequest, background_tasks: BackgroundTasks):
    task_id = PersonaBuildService.create_task(request.topic)
    background_tasks.add_task(PersonaBuildService.process_task, task_id, request.topic)
    return PersonaBuildService.get_task_status(task_id)

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    try:
        task = PersonaBuildService.get_task_status(task_id)
        return task
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")