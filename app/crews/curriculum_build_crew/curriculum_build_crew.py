import os
from dotenv import load_dotenv
load_dotenv()
from langtrace_python_sdk import langtrace
lang_api_key = os.getenv("LANGTRACE_API_KEY")
langtrace.init(api_key = lang_api_key)

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from tools.course_tool import OnlineCourseTool
from tools.video_tool import VideoTool
from crewai_tools import SerperDevTool

@CrewBase
class CurriculumBuilderCrew():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    openai_model = LLM(
        model=f"{os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')}", 
        temperature=0.2,
        max_tokens=500
    )

    @agent
    def input_ingestion_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['input_ingestion_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def curriculum_structuring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['curriculum_structuring_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def scheduler_duration_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scheduler_duration_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def resource_aggregation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_aggregation_agent'],
            tools=[OnlineCourseTool(), VideoTool()],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def coordination_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['coordination_agent'],
            verbose=True,
            llm=self.openai_model
        )

    @agent
    def quality_assurance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_assurance_agent'],
            verbose=True,
            llm=self.openai_model
        )
    
    @task
    def input_ingestion_task(self) -> Task:
        return Task(
            config=self.tasks_config['input_ingestion_task'],
        )

    @task
    def curriculum_structuring_task(self) -> Task:
        return Task(
            config=self.tasks_config['curriculum_structuring_task'],
        )

    @task
    def scheduler_duration_task(self) -> Task:
        return Task(
            config=self.tasks_config['scheduler_duration_task'],
        )

    @task
    def resource_aggregation_task(self) -> Task:
        return Task(
            config=self.tasks_config['resource_aggregation_task'],
        )

    @task
    def coordination_task(self) -> Task:
        return Task(
            config=self.tasks_config['coordination_task'],
        )

    @task
    def quality_assurance_task(self) -> Task:
        return Task(
            config=self.tasks_config['quality_assurance_task'],
            output_file='app/outputs/curriculum.md'
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            name="Curriculum Build Crew"
        )