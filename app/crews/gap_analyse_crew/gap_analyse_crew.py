import os
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Agent, Process, LLM
from crewai_tools import JSONSearchTool, WebsiteSearchTool
from crewai.project import CrewBase, agent, crew, task

load_dotenv()

# Suppress logs from LiteLLM and httpx
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

@CrewBase
class GapAnalyseCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    llm_config = {
        "api_key": os.getenv('OPENAI_API_KEY'),
        "model": os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini'),
        "temperature": 0.2,
        "max_tokens": 500
    }

    openai_model = LLM(
        model=f"{os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')}", 
        temperature=0.2,
        max_tokens=500
    )

    json_tool = JSONSearchTool()
    web_tool = WebsiteSearchTool()
    
    @agent
    def user_persona_reader(self) -> Agent:
        return Agent(
            config=self.agents_config['user_persona_reader'],
            verbose=True,
            allow_delegation=False,
            memory=True,
            tools=[self.json_tool],
        )
    
    @agent
    def project_requirement_reader(self) -> Agent:
        return Agent(
            config=self.agents_config['project_requirement_reader'],
            verbose=True,
            allow_delegation=False,
            memory=True,
            tools=[self.json_tool],
        )
    
    @agent
    def software_domain_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['software_domain_expert'],
            verbose=True,
            allow_delegation=False,
            memory=True,
            tools=[self.web_tool],
        )
    
    @agent
    def gap_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['gap_analyzer'],
            verbose=True,
            allow_delegation=False,
            memory=True,
            tools=[self.web_tool],
        )
    
    @agent
    def gap_report_formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['gap_report_formatter'],
            verbose=True,
            allow_delegation=False,
            memory=True,
            tools=[self.json_tool],
        )
    
    @agent
    def gap_report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['gap_report_generator'],
            verbose=True,
            allow_delegation=False,
            memory=True,
        )
    
    @task
    def extract_skills_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_skills_task'],
            agent=self.user_persona_reader()
        )
    
    @task
    def normalize_skills_task(self) -> Task:
        return Task(
            config=self.tasks_config['normalize_skills_task'],
            agent=self.user_persona_reader(),
            context=[self.extract_skills_task()]
        )

    @task
    def categorize_skills_task(self) -> Task:
        return Task(
            config=self.tasks_config['categorize_skills_task'],
            agent=self.user_persona_reader(),
            context=[self.normalize_skills_task()]
        )
    
    @task
    def extract_explicit_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_explicit_requirements_task'],
            agent=self.project_requirement_reader()
        )
    
    @task
    def infer_implicit_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['infer_implicit_requirements_task'],
            agent=self.project_requirement_reader(),
            context=[self.extract_explicit_requirements_task()]
        )
    
    @task
    def normalize_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['normalize_requirements_task'],
            agent=self.project_requirement_reader(),
            context=[self.extract_explicit_requirements_task(), self.infer_implicit_requirements_task()]
        )
    
    @task
    def validate_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_requirements_task'],
            agent=self.software_domain_expert(),
            context=[self.normalize_requirements_task()]
        )
    
    @task
    def define_dependencies_task(self) -> Task:
        return Task(
            config=self.tasks_config['define_dependencies_task'],
            agent=self.software_domain_expert(),
            context=[self.validate_requirements_task()]
        )
    
    @task
    def contextualize_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['contextualize_requirements_task'],
            agent=self.software_domain_expert(),
            context=[self.define_dependencies_task()]
        )
    
    @task
    def compare_skills_task(self) -> Task:
        return Task(
            config=self.tasks_config['compare_skills_task'],
            agent=self.gap_analyzer(),
            context=[self.contextualize_requirements_task(), self.categorize_skills_task()]
        )
    
    @task
    def categorize_gaps_task(self) -> Task:
        return Task(
            config=self.tasks_config['categorize_gaps_task'],
            agent=self.gap_analyzer(),
            context=[self.compare_skills_task()]
        )
    
    @task
    def structure_gap_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['structure_gap_analysis_task'],
            agent=self.gap_analyzer(),
            context=[self.categorize_gaps_task()]
        )
    
    @task
    def organize_gap_info_task(self) -> Task:
        return Task(
            config=self.tasks_config['organize_gap_info_task'],
            agent=self.gap_analyzer(),
            context=[self.structure_gap_analysis_task()]
        )
    
    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            agent=self.gap_report_generator(),
            context=[self.organize_gap_info_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            llm_config=self.llm_config
        )
