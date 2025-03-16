import logging
from app.services.task_service import TaskService
from app.crews.persona_build_crew.persona_build_crew import PersonaBuildCrew

logger = logging.getLogger(__name__)

class PersonaBuildService(TaskService):
    @classmethod
    async def run_crew(cls, task_id: str, topic: str):
        crew = PersonaBuildCrew()
        result = await crew.crew().kickoff_async(inputs={"topic": topic})
        cls._tasks[task_id].result = result 