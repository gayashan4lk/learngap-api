from fastapi import APIRouter
from app.models.userModels import UserVM
from app.ai_workflows.persona_build_crew import PersonaBuildCrew

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