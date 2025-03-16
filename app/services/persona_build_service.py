import asyncio
import uuid
import logging
from typing import Dict
from app.models.task_models import TaskResponse, TaskStatus
from app.crews.persona_build_crew.persona_build_crew import PersonaBuildCrew
from app.models.user_models import UserPersonaRequest

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class PersonaBuildService():
    _tasks: Dict[str, TaskResponse] = {}

    @classmethod
    def create_task(cls) -> str:
        task_id = str(uuid.uuid4())
        cls._tasks[task_id] = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,   
        )
        logger.info(f"Task {task_id} created with status {TaskStatus.PENDING}")
        return task_id
    
    @classmethod
    def get_task_status(cls, task_id: str) -> TaskResponse:
        if task_id not in cls._tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        return cls._tasks.get(task_id)
    
    @classmethod
    async def process_task(cls, task_id: str, request: UserPersonaRequest):
        try:
            cls._tasks[task_id].status = TaskStatus.PROCESSING
            logger.info(f"Task {task_id} status changed to PROCESSING")
            print(f"request: {request}")
            print(f"request.model_dump(): {request.model_dump()}")
            crew = PersonaBuildCrew()
            logger.info(f"Running {crew.crew().name} for task {task_id}")
            result = await crew.crew().kickoff_async(inputs=request.model_dump())
            logger.info(f"Run {crew.crew().name} completed")
            cls._tasks[task_id].status = TaskStatus.COMPLETED
            cls._tasks[task_id].result = result
            logger.info(f"Task {task_id} completed successfully with status {cls._tasks[task_id].status}")
        except Exception as e:
            cls._tasks[task_id].status = TaskStatus.FAILED
            cls._tasks[task_id].error = str(e)
            logger.error(f"Task {task_id} failed with error: {e}")
