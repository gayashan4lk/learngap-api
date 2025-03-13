import warnings
from fastapi import APIRouter
from app.models.user_models import UserVM

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
    # output = PersonaBuildCrew().crew().kickoff()
    return user_data