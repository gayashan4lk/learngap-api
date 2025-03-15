import asyncio
import uuid
import logging
import os
import json
import traceback
import re
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
    def clean_markdown_json(cls, content):
        """Remove markdown code block markers from JSON content"""
        logger.info("Cleaning markdown from JSON content")
        
        # Check if content is already a string
        if not isinstance(content, str):
            logger.info(f"Content is not a string, type: {type(content)}")
            return content
            
        # Remove markdown code block markers
        # Pattern matches ```json at the start and ``` at the end
        content = re.sub(r'^```(?:json)?\s*\n', '', content.strip())
        content = re.sub(r'\n```\s*$', '', content.strip())
        
        # Log a preview of the cleaned content
        logger.info(f"Cleaned content preview: {content[:100]}...")
        
        return content
    
    @classmethod
    def process_output(cls, result, description, temp_dir):
        """Process the output from the crew"""
        try:
            # Check if skill_analysis_result.json was created by the crew
            json_output_path = os.path.join(temp_dir, "skill_analysis_result.json")
            
            logger.info(f"Checking for crew output at: {json_output_path}")
            
            if os.path.exists(json_output_path):
                logger.info(f"Found crew output file at: {json_output_path}")
                with open(json_output_path, 'r') as f:
                    content = f.read()
                    
                # Clean markdown formatting from content
                cleaned_content = cls.clean_markdown_json(content)
                    
                try:
                    # Try to parse the cleaned content as JSON
                    result = json.loads(cleaned_content)
                    logger.info(f"Successfully loaded JSON from cleaned file content")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from cleaned file: {e}")
                    # Log the cleaned content for debugging
                    logger.error(f"Cleaned content preview: {cleaned_content[:500]}...")
                    result = {"raw_output": cleaned_content}
            else:
                logger.warning(f"No output file found at: {json_output_path}")
                
            # Make sure the result is a dictionary
            if not isinstance(result, dict):
                logger.warning(f"Result is not a dictionary, converting. Type: {type(result)}")
                if isinstance(result, str):
                    # Log the string content for debugging
                    logger.info(f"Result string: {result[:500]}...")
                    
                    # Clean markdown formatting if present
                    cleaned_result = cls.clean_markdown_json(result)
                    
                    # Try to parse it as JSON if it looks like JSON
                    if cleaned_result.strip().startswith('{') and cleaned_result.strip().endswith('}'):
                        try:
                            result = json.loads(cleaned_result)
                        except json.JSONDecodeError:
                            result = {"raw_output": cleaned_result}
                    else:
                        result = {"raw_output": cleaned_result}
                else:
                    result = {"raw_output": str(result)}
            
            # Ensure the required structure is present
            if "position" not in result:
                result["position"] = "Unknown Position"
            if "description" not in result:
                result["description"] = description
            if "required_skills" not in result:
                result["required_skills"] = {"technical": {}, "non_technical": {}}
                
            # If we have raw_output, try to extract skills from it
            if "raw_output" in result and not result["required_skills"]["technical"] and not result["required_skills"]["non_technical"]:
                logger.info("Attempting to extract skills from raw output")
                
                # Try to extract JSON from the raw output using regex
                json_pattern = r'({[\s\S]*})'
                json_matches = re.search(json_pattern, result["raw_output"])
                
                if json_matches:
                    try:
                        extracted_json = json_matches.group(1)
                        parsed_json = json.loads(extracted_json)
                        logger.info(f"Successfully extracted JSON from raw output")
                        
                        # Update result with extracted data
                        if isinstance(parsed_json, dict):
                            for key, value in parsed_json.items():
                                result[key] = value
                            
                            # Remove raw_output if we successfully extracted JSON
                            if "required_skills" in parsed_json:
                                del result["raw_output"]
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse extracted JSON from raw output")
                
                # If extraction failed or no JSON found, create a minimal structure
                if "raw_output" in result:
                    # A simple extraction structure
                    result["required_skills"] = {
                        "technical": {"extracted_skills": {"skills": []}},
                        "non_technical": {"extracted_skills": {"skills": []}}
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing output: {e}")
            logger.error(traceback.format_exc())
            return {
                "position": "Error Processing Output",
                "description": description,
                "required_skills": {
                    "technical": {},
                    "non_technical": {}
                },
                "error": str(e)
            }

    @classmethod
    def save_json_file(cls, data, file_path):
        """Save JSON data to file with error handling"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Successfully saved JSON to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON to {file_path}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    @classmethod
    async def process_task(cls, task_id: str, description: str):
        """Process a goal refinement task"""
        original_dir = os.getcwd()
        temp_dir = None
        
        try:
            # Update task status
            cls._tasks[task_id].status = TaskStatus.PROCESSING
            logger.info(f"Goal Refine Task {task_id} status changed to PROCESSING")
            
            # Get base paths using absolute paths
            base_dir = os.path.abspath(os.path.join(original_dir))
            logger.info(f"Base directory: {base_dir}")
            
            # Create directory paths
            output_dir = os.path.join(base_dir, "app", "outputs")
            goals_dir = os.path.join(output_dir, "goals")
            temp_dir = os.path.join(output_dir, f"temp_{task_id}")
            
            # Create directories
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(goals_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Log directory status
            logger.info(f"Created output directory: {output_dir}, exists: {os.path.exists(output_dir)}")
            logger.info(f"Created goals directory: {goals_dir}, exists: {os.path.exists(goals_dir)}")
            logger.info(f"Created temp directory: {temp_dir}, exists: {os.path.exists(temp_dir)}")
            
            # Change to temp directory for crew processing
            os.chdir(temp_dir)
            logger.info(f"Changed working directory to: {os.getcwd()}")
            
            # Initialize and run the crew
            crew_instance = GoalRefineCrew()
            crew = crew_instance.crew(inputs={"description": description})
            
            try:
                # Run the crew
                result = await crew.kickoff_async()
                logger.info(f"Crew completed successfully, result type: {type(result)}")
                if isinstance(result, str):
                    logger.info(f"String result preview: {result[:200]}...")
                elif isinstance(result, dict):
                    logger.info(f"Dict result keys: {list(result.keys())}")
            except Exception as e:
                logger.error(f"Error during crew execution: {e}")
                logger.error(traceback.format_exc())
                result = {"error": str(e)}
            
            # Process the output
            formatted_output = cls.process_output(result, description, temp_dir)
            
            # Return to original directory before file operations
            os.chdir(original_dir)
            logger.info(f"Returned to original directory: {os.getcwd()}")
            
            # Save output file to goals directory
            output_file = os.path.join(goals_dir, f"{task_id}.json")
            save_success = cls.save_json_file(formatted_output, output_file)
            
            # Update task status
            if save_success:
                cls._tasks[task_id].status = TaskStatus.COMPLETED
                cls._tasks[task_id].result = {
                    "output": formatted_output,
                    "output_file": output_file
                }
                logger.info(f"Goal Refine Task {task_id} completed successfully")
            else:
                cls._tasks[task_id].status = TaskStatus.FAILED
                cls._tasks[task_id].error = "Failed to save output file"
                logger.error(f"Goal Refine Task {task_id} failed: Could not save output file")
            
        except Exception as e:
            # Log the full error with traceback
            logger.error(f"Goal Refine Task {task_id} failed with error: {e}")
            logger.error(traceback.format_exc())
            
            # Update task status
            cls._tasks[task_id].status = TaskStatus.FAILED
            cls._tasks[task_id].error = str(e)
            
        finally:
            # Always ensure we return to the original directory
            try:
                os.chdir(original_dir)
                logger.info(f"Ensured return to original directory: {os.getcwd()}")
            except Exception as e:
                logger.error(f"Error returning to original directory: {e}")
            
            # Clean up temp directory
            try:
                if temp_dir and os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")
                
        # Return the final task status
        return cls.get_task_status(task_id) 