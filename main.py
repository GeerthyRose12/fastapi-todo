from fastapi import FastAPI

from app.db.database import engine, Base
from app.models.todo import Todo
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Welcome to my Todo API"}

@app.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo

@app.get("/todos", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()

    return todos

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    return todo

@app.put(
    "/todos/{todo_id}",
    response_model=TodoResponse
)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db)
):
    todo = (
        db.query(Todo)
        .filter(Todo.id == todo_id)
        .first()
    )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    todo.title = todo_data.title
    todo.description = todo_data.description
    todo.completed = todo_data.completed

    db.commit()
    db.refresh(todo)

    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    todo = (
        db.query(Todo)
        .filter(Todo.id == todo_id)
        .first()
    )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    db.delete(todo)
    db.commit()

    return {
        "message": "Todo deleted successfully"
    }