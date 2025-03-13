from fastapi import FastAPI

from app.routers import test
from app.routers import workflows

app = FastAPI()

app.include_router(test.router)
app.include_router(workflows.router)

@app.get("/")
async def root():
    return {"message": "Hello world!"}
