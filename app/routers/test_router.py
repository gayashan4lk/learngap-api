from fastapi import APIRouter

router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def test():
    return {"message": "LearnGap API is running"}

@router.get("/items")
async def get_items():
    return {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}