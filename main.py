from fastapi import FastAPI

from app.db.database import engine, Base
from app.models.todo import Todo
from app.models.user import User
from app.routers import todo,user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(todo.router)
app.include_router(user.router)


@app.get("/")
def home():
    return {"message": "Welcome to my Todo API"}
