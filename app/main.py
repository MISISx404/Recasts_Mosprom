# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.routes import posts, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RecSys API", version="1.0.0")

app.include_router(posts.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"status": "ok"}
