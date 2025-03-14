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
    
    @agent
    def agent1(self) -> Agent:
        return Agent(
            config=self.agents_config['agent1'],
            verbose=True,
        )
    
    @agent
    def agent2(self) -> Agent:
        return Agent(
            config=self.agents_config['agent2'],
            verbose=True,
        )
    
    @task
    def task1(self) -> Task:
        return Task(
            config=self.tasks_config['task1'],
            agent=self.agent1()
        )
    
    @task
    def task2(self) -> Task:
        return Task(
            config=self.tasks_config['task2'],
            agent=self.agent2()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )