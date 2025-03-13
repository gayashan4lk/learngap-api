from fastapi import APIRouter
from app.models.userModels import UserVM

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
    return user_data