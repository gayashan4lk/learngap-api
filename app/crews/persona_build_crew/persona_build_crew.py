import os
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Agent, Process, LLM
from crewai.project import CrewBase, agent, crew, task
# from crewai_tools import SerperDevTool


load_dotenv()

# Suppress logs from LiteLLM and httpx
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

@CrewBase
class PersonaBuildCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # search_tool = SerperDevTool()

    anthropic_model_haiku = LLM(
		model=f"anthropic/{os.getenv('ANTHROPIC_MODEL_HAIKU', 'claude-3-5-haiku-latest')}", 
        temperature=0.5,
        max_tokens=1000
    )
    anthropic_model_sonnet = LLM(
		model=f"anthropic/{os.getenv('ANTHROPIC_MODEL_SONNET', 'claude-3-7-sonnet-latest')}", 
        temperature=0.5,
        max_tokens=1000
    )
    
    @agent
    def user_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['user_data_analyst'],
            verbose=True,
            # tools=[self.search_tool],
            # llm=self.anthropic_model_haiku
        )
    
    @agent
    def user_data_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['user_data_reporter'],
            verbose=True,
            # llm=self.anthropic_model_haiku
        )
    
    @task
    def user_data_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_data_analyst_task'],
            agent=self.user_data_analyst()
        )
    
    @task
    def user_data_reporter_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_data_reporter_task'],
            agent=self.user_data_reporter(),
            output_file='app/outputs/report.md'
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            name="Persona Build Crew"
        )
    