from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/todos", tags=["Todos"])


def get_todo_or_404(todo_id: int, db: Session = Depends(get_db)) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(**todo.model_dump(), user_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@router.get("", response_model=list[TodoResponse])
def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    completed: bool | None = None,
    search: str | None = None
):
    query = db.query(Todo).filter(Todo.user_id == current_user.id)

    if completed is not None:
        query = query.filter(Todo.completed == completed)
    if search is not None:
        query = query.filter(Todo.title.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo: Todo = Depends(get_todo_or_404), current_user: User = Depends(get_current_user)):
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_data: TodoUpdate, todo: Todo = Depends(get_todo_or_404), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in todo_data.model_dump().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo: Todo = Depends(get_todo_or_404), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(todo)
    db.commit()
