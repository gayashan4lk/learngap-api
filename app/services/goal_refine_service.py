import asyncio
import uuid
import logging
import os
from typing import Dict
from pathlib import Path
from app.models.task_models import TaskStatus, TaskResponse
from app.crews.goal_refine_crew.goal_refine_crew import Proj as GoalRefineCrew

# configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class GoalRefineService:
    _tasks: Dict[str, TaskResponse] = {}

    @classmethod
    def create_task(cls, description: str) -> str:
        task_id = str(uuid.uuid4())
        cls._tasks[task_id] = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,   
        )
        logger.info(f"Goal Refine Task {task_id} created with status {TaskStatus.PENDING} for description: {description[:50]}...")
        return task_id
    
    @classmethod
    def get_task_status(cls, task_id: str) -> TaskResponse:
        if task_id not in cls._tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        return cls._tasks.get(task_id)
    
    @classmethod
    async def process_task(cls, task_id: str, description: str):
        try:
            cls._tasks[task_id].status = TaskStatus.PROCESSING
            logger.info(f"Goal Refine Task {task_id} status changed to PROCESSING")
            
            # Create the output directory if it doesn't exist
            output_dir = Path("app/outputs")
            output_dir.mkdir(exist_ok=True)
            
            # Create a task-specific output directory
            task_output_dir = output_dir / task_id
            task_output_dir.mkdir(exist_ok=True)
            
            # Save the current working directory
            original_dir = os.getcwd()
            
            try:
                # Set the current working directory to the task output directory for the crew
                os.chdir(task_output_dir)
                
                # Initialize crew and process the task
                crew_instance = GoalRefineCrew()
                crew = crew_instance.crew(inputs={"description": description})
                result = await crew.kickoff_async()
                
            finally:
                # Reset the working directory
                os.chdir(original_dir)
            
            # Update task status
            cls._tasks[task_id].status = TaskStatus.COMPLETED
            cls._tasks[task_id].result = {
                "output": result,
                "output_path": str(task_output_dir)
            }
            logger.info(f"Goal Refine Task {task_id} completed successfully with status {cls._tasks[task_id].status}")
        except Exception as e:
            cls._tasks[task_id].status = TaskStatus.FAILED
            cls._tasks[task_id].error = str(e)
            logger.error(f"Goal Refine Task {task_id} failed with error: {e}") 