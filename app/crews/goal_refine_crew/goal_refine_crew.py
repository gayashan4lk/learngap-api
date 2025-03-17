import os
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Agent, Process, LLM
from crewai.project import CrewBase, agent, crew, task

load_dotenv()

# Suppress logs from LiteLLM and httpx
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

@CrewBase
class GoalRefineCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    openai_model = LLM(
        model=f"{os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')}", 
        temperature=0.2,
        max_tokens=500
    )
    
    @agent
    def input_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['input_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def refining_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['refining_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analysis_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def output_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['output_agent'],
            verbose=True,
            llm=self.openai_model
        )
    
    @task
    def input_task(self) -> Task:
        return Task(
            config=self.tasks_config['input_task'],
            agent=self.input_agent()
        )

    @task
    def refinement_task(self) -> Task:
        return Task(
            config=self.tasks_config['refinement_task'],
            agent=self.refining_agent(),
            context=[self.input_task()]
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            agent=self.analysis_agent(),
            context=[self.refinement_task()]
        )

    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['validation_task'],
            agent=self.validation_agent(),
            context=[self.analysis_task(), self.refinement_task()]
        )

    @task
    def output_task(self) -> Task:
        """Create a task for the output agent that writes JSON directly to a file."""
        return Task(
            config=self.tasks_config['output_task'],
            agent=self.output_agent(),
            context=[self.validation_task(), self.analysis_task(), self.refinement_task()],
            output_file='app/outputs/goal_refine_result.json',
            # Add a callback to sanitize and save the output as valid JSON
            async_callbacks=[self.save_output_as_json]
        )
        
    async def save_output_as_json(self, output):
        """Callback to save the raw output as a valid JSON file."""
        import json
        import re
        import os
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Try to extract JSON from the output
            if isinstance(output, str):
                # Clean the output by removing any markdown or backticks
                cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', output)
                # Find JSON content between braces
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        # Parse to ensure it's valid, then format it nicely
                        parsed = json.loads(json_str)
                        # Ensure we have the correct structure
                        if isinstance(parsed, dict):
                            if "description" not in parsed:
                                # Get description from input if available
                                if hasattr(self, 'inputs') and isinstance(self.inputs, dict) and 'description' in self.inputs:
                                    parsed["description"] = self.inputs["description"]
                                else:
                                    parsed["description"] = "Unknown"
                            if "required_skills" not in parsed:
                                parsed["required_skills"] = {
                                    "technical": {},
                                    "non_technical": {}
                                }
                            
                            # Write to the file
                            with open('app/outputs/goal_refine_result.json', 'w') as f:
                                json.dump(parsed, f, indent=2)
                                logger.info(f"Successfully wrote JSON to goal_refine_result.json")
                                return output
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse JSON from output")
            
            # Fallback if we couldn't extract valid JSON
            logger.warning("Could not extract valid JSON from output, using fallback")
            fallback = {
                "description": getattr(self.inputs, 'description', "Unknown"),
                "required_skills": {
                    "technical": {},
                    "non_technical": {}
                }
            }
            with open('app/outputs/goal_refine_result.json', 'w') as f:
                json.dump(fallback, f, indent=2)
                
            return output
        except Exception as e:
            logger.error(f"Error in save_output_as_json: {str(e)}")
            return output
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            name="Goal Refine Crew"
        )