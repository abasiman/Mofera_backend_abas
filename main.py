

import models
import auth
import centra
import guard_harbor
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, status

from sqlalchemy.orm import Session
from typing import List, Annotated
from pydantic import BaseModel, Field
from database import SessionLocal, engine
from datetime import date
from models import Users

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from auth import router


import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app = FastAPI()

router = APIRouter()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Oops! That resource does not exist."},
        )
    else:
        content = {"message": exc.detail}
        return JSONResponse(status_code=exc.status_code, content=content)
    return await request.app.default_exception_handler(request, exc)


app.include_router(auth.router)
app.include_router(centra.router)
app.include_router(guard_harbor.router)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://mofera-frontend-seven.vercel.app",
    # add other origins here


]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: None, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}

if __name__ == '__main__':
    uvicorn.run("main:app", host = "127.0.0.1", reload=True)
