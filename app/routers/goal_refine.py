from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from app.models.task_models import TaskStatus, TaskResponse
from app.services.goal_refine_service import GoalRefineService
from pydantic import BaseModel
import json
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GoalRefineRequest(BaseModel):
    description: str

class GoalRefineResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    output_file: Optional[str] = None

router = APIRouter(
    prefix="/goal_refine",
    tags=["goal_refine"],
    responses={404: {"description": "Not found"}},
)
    
@router.post("/", response_model=GoalRefineResponse)
async def create_goal_refine_task(request: GoalRefineRequest, background_tasks: BackgroundTasks):
    try:
        task_id = GoalRefineService.create_task(request.description)
        background_tasks.add_task(GoalRefineService.process_task, task_id, request.description)
        task = GoalRefineService.get_task_status(task_id)
        
        return GoalRefineResponse(
            task_id=task.task_id,
            status=task.status.value,
            result=None,
            error=getattr(task, 'error', None)
        )
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create task: {str(e)}"}
        )

@router.get("/{task_id}", response_model=GoalRefineResponse)
async def get_goal_refine_task(task_id: str):
    try:
        # Try to get the task status
        try:
            task = GoalRefineService.get_task_status(task_id)
        except ValueError:
            # Task not found
            raise HTTPException(status_code=404, detail="Task not found")
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            # Return a more graceful error response
            return GoalRefineResponse(
                task_id=task_id,
                status="error",
                error=f"Error retrieving task: {str(e)}"
            )
            
        # Create the initial response with basic info
        response = GoalRefineResponse(
            task_id=task_id,
            status=task.status.value,
            error=getattr(task, 'error', None)
        )
        
        # Add result only if it exists and task is completed
        if task.status.value == "completed" and hasattr(task, 'result') and task.result:
            try:
                # Get the output file path
                output_file = task.result.get('output_file')
                response.output_file = output_file
                
                # Get the output data
                if 'output' in task.result:
                    response.result = task.result['output']
                
                # Try to read from file if it exists for most up-to-date data
                if output_file and os.path.exists(output_file):
                    try:
                        with open(output_file, 'r') as f:
                            file_data = json.load(f)
                            response.result = file_data
                    except Exception as e:
                        logger.warning(f"Could not read output file {output_file}: {str(e)}")
                        # Keep using the result from the task object
            except Exception as file_error:
                logger.warning(f"Error reading result data: {str(file_error)}")
                # Don't fail, just continue with what we have
        
        return response
    except HTTPException:
        # Pass through HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Unexpected error handling task {task_id}: {str(e)}")
        # Return a response instead of an error
        return GoalRefineResponse(
            task_id=task_id,
            status="error",
            error=f"Error processing request: {str(e)}"
        )
