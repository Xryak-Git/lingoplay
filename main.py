# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4, UUID

app = FastAPI()

class Task(BaseModel):
    id: UUID
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str

# Временное хранилище
tasks: List[Task] = []

@app.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate):
    new_task = Task(id=uuid4(), title=task.title)
    tasks.append(new_task)
    return new_task

@app.get("/tasks/", response_model=List[Task])
def list_tasks():
    return tasks

@app.delete("/tasks/{task_id}")
def delete_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return {"detail": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")
