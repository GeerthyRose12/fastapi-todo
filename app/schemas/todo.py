from pydantic import BaseModel, ConfigDict


class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool

    model_config = ConfigDict(from_attributes=True)