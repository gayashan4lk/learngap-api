import warnings
from fastapi import APIRouter
from app.models.user_models import UserVM

# TODO: when import this it's giving me a warning in uvicorn
# TODO: I need to figure out how to fix this
from app.ai_workflows.persona_build_crew import PersonaBuildCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def test():
    return {"message": "AI workflows are running"}

@router.post("/persona")
async def persona_builder(user_data: UserVM):
    output = PersonaBuildCrew().crew().kickoff()
    return output