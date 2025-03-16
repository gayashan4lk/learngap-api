from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.persona_build_router import router as persona_build_router
from app.routers.goal_refine_router import router as goal_refine_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(persona_build_router)
app.include_router(goal_refine_router)
@app.get("/")
async def root():
    return {"message": "LearnGap API is running"}

@app.post("/test")
async def test():
    return {"message": "Test"}
