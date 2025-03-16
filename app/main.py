from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.test import router as test_router
from app.routers.workflows import router as workflows_router

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

@app.get("/hello")
async def root():
    return {"message": "Hello world!"}
