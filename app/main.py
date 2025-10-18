# app/main.py
from fastapi import FastAPI
from .database import engine, Base
from .routes import posts, users
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RecSys API", version="1.0.0")

app.include_router(posts.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"status": "ok"}
