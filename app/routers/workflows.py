from fastapi import APIRouter

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def test():
    return {"message": "AI workflows are running"}

@router.post("/persona")
async def persona_builder():
    return {"message": "Persona builder is running"}