import asyncio
import uuid
import logging
from typing import Dict, ClassVar
from app.models.task_models import TaskStatus, TaskResponse
from abc import ABC, abstractmethod

# configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TaskService(ABC):
    _tasks: ClassVar[Dict[str, TaskResponse]] = {}

    @classmethod
    def create_task(cls, topic: str) -> str:
        task_id = str(uuid.uuid4())
        cls._tasks[task_id] = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,   
        )
        logger.info(f"Task {task_id} created with status {TaskStatus.PENDING} for topic {topic}")
        return task_id
    
    @classmethod
    def get_task_status(cls, task_id: str) -> TaskResponse:
        if task_id not in cls._tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        return cls._tasks.get(task_id)
    
    @classmethod
    async def process_task(cls, task_id: str, topic: str):
        try:
            cls._tasks[task_id].status = TaskStatus.PROCESSING
            logger.info(f"Task {task_id} status changed to PROCESSING")
            
            # Implementation to be provided by child classes
            await cls.run_crew(task_id, topic)
            
            cls._tasks[task_id].status = TaskStatus.COMPLETED
            logger.info(f"Task {task_id} completed successfully with status {cls._tasks[task_id].status}")
        except Exception as e:
            cls._tasks[task_id].status = TaskStatus.FAILED
            cls._tasks[task_id].error = str(e)
            logger.error(f"Task {task_id} failed with error: {e}")
    
    @classmethod
    @abstractmethod
    async def run_crew(cls, task_id: str, topic: str):
        pass
