import os
import logging
from dotenv import load_dotenv
from crewai import Crew, Task, Agent, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FirecrawlCrawlWebsiteTool, FirecrawlSearchTool


load_dotenv()

# Suppress logs from LiteLLM and httpx
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

@CrewBase
class PersonaBuildCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    search_tool = SerperDevTool()
    # general_web_scrape_tool = ScrapeWebsiteTool()
    # github_scrape_tool = ScrapeWebsiteTool(website_url='https://github.com/')
    # medium_scrape_tool = ScrapeWebsiteTool(website_url='https://medium.com/')
    # github_firecrawl_crawl_tool = FirecrawlCrawlWebsiteTool(
    #     website_url='https://github.com/DK01git/LearnA_ws',
    #     max_depth=2,
    #     onlyMainContent=True
    # )
    # linkedin_firecrawl_crawl_tool = FirecrawlCrawlWebsiteTool(
    #     website_url='https://rocketreach.co/diluksha-perera-email_719639221/',
    #     max_depth=2,
    #     onlyMainContent=True
    # )
    # medium_firecrawl_crawl_tool = FirecrawlCrawlWebsiteTool(
    #     website_url='https://medium.com/@dilukshakaushal',
    #     max_depth=2,
    #     onlyMainContent=True
    # )

    # firecrawl_search_tool = FirecrawlSearchTool(query='what is firecrawl?')

    anthropic_model_haiku = LLM(
		model=f"anthropic/{os.getenv('ANTHROPIC_MODEL_HAIKU', 'claude-3-5-haiku-latest')}", 
        temperature=0.1,
        max_tokens=1000
    )
    anthropic_model_sonnet = LLM(
		model=f"anthropic/{os.getenv('ANTHROPIC_MODEL_SONNET', 'claude-3-7-sonnet-latest')}", 
        temperature=0.1,
        max_tokens=1000
    )

    openai_model = LLM(
        model=f"{os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')}", 
        temperature=0.1,
        max_tokens=1000
    )
    
    @agent
    def profile_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['profile_finder'],
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )
    
    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )
    
    @agent
    def linkedin_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['linkedin_specialist'],
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )
    
    @agent
    def github_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['github_analyst'],
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )
    
    @agent
    def content_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['content_analyst'],
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )
    
    @agent
    def data_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['data_synthesizer'],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )
    
    @agent
    def persona_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['persona_generator'],
            allow_delegation=False,
            verbose=True,
            llm=self.openai_model
        )

    @task
    def task_initial_data_collection(self) -> Task:
        return Task(
            config=self.tasks_config['task_initial_data_collection'],
            agent=self.profile_finder(),
            tools=[self.search_tool]
        )
    
    @task
    def task_web_search(self) -> Task:
        return Task(
            config=self.tasks_config['task_web_search'],
            agent=self.web_researcher(),
            tools=[self.search_tool],
            dependencies=[self.task_initial_data_collection()]
        )
    
    @task
    def task_linkedin_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['task_linkedin_analysis'],
            agent=self.linkedin_specialist(),
            tools=[self.search_tool],
            dependencies=[self.task_initial_data_collection()]
        )
    
    @task
    def task_github_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['task_github_analysis'],
            agent=self.github_analyst(),
            tools=[self.search_tool],
            dependencies=[self.task_initial_data_collection()]
        )
    
    @task
    def task_medium_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['task_medium_analysis'],
            agent=self.content_analyst(),
            tools=[self.search_tool],
            dependencies=[self.task_initial_data_collection()]
        )
    
    @task
    def task_synthesize_user_profile(self) -> Task:
        return Task(
            config=self.tasks_config['task_synthesize_user_profile'],
            agent=self.data_synthesizer(),
            dependencies=[self.task_initial_data_collection(), self.task_web_search(), self.task_linkedin_analysis(), self.task_github_analysis(), self.task_medium_analysis()]
        )
    
    @task
    def task_persona_generation(self) -> Task:
        return Task(
            config=self.tasks_config['task_persona_generation'],
            agent=self.persona_generator(),
            dependencies=[self.task_synthesize_user_profile()]
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
    