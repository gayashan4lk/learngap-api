from crewai import LLM, Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os

load_dotenv()

@CrewBase
class PersonaBuildCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    anthropic_model_haiku = LLM(
		model=f"anthropic/{os.getenv('ANTHROPIC_MODEL_HAIKU', 'claude-3-5-haiku-latest')}", temperature=0.5)
    anthropic_model_sonnet = LLM(
		model=f"anthropic/{os.getenv('ANTHROPIC_MODEL_SONNET', 'claude-3-7-sonnet-latest')}", temperature=0.5)

    @agent
    def user_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['user_data_analyst'],
            verbose=True,
            llm=self.anthropic_model_haiku
        )
    
    @agent
    def user_data_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['user_data_reporter'],
            verbose=True,
            llm=self.anthropic_model_haiku
        )
    
    @task
    def user_data_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_data_analyst_task'],
        )
    
    @task
    def user_data_reporter_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_data_reporter_task'],
            output_file='report.md'
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
    
