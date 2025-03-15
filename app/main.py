from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.test import router as test_router
from app.routers.workflows import router as workflows_router
from app.routers.goal_refine import router as goal_refine_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router)
app.include_router(workflows_router)
app.include_router(goal_refine_router)

@app.get("/")
async def root():
    return {"message": "Hello world!"}
