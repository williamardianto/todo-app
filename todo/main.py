from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime
from typing import List
from infra.redis_repository import RedisRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await repository.connect()
    yield
    await repository.close()


app = FastAPI(lifespan=lifespan)
repository = RedisRepository()


class Todo(BaseModel):
    id: int
    title: str
    description: str = None
    created_at: str = None
    due_date: str = None
    completed: bool = False


@app.post("/todos/", response_model=Todo)
async def create_todo(todo: Todo):
    todo.id = await repository.redis.incr("todo:counter")
    todo.created_at = str(datetime.now())
    await repository.save_todo(f"todo:{todo.id}", todo.model_dump())
    return todo


@app.get("/todos/", response_model=List[Todo])
async def get_all_todos():
    todos = await repository.get_all_todos()
    return [Todo(**todo_data) for todo_data in todos]


@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo_by_id(todo_id: int):
    todo_data = await repository.get_todo_by_id(todo_id)
    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")
    return Todo(**todo_data)


@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, updated_todo: Todo):
    updated_todo_data = updated_todo.model_dump()
    updated_todo_data.pop("id", None)
    if not await repository.update_todo(todo_id, updated_todo_data):
        raise HTTPException(status_code=404, detail="Todo not found")
    updated_todo.id = todo_id
    return updated_todo


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    if not await repository.delete_todo(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}
