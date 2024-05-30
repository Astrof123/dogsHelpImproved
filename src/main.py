from fastapi import FastAPI, APIRouter, Body, Query, HTTPException
import uvicorn
from src.database import BaseDBModel, engine
from src.users.user_router import router as user_router

BaseDBModel.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Hello World!!!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)