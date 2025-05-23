from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4

app = FastAPI()

# In-memory storage for tasks
db_tasks: List["Task"] = []

# Pydantic Models
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str # e.g., "pending", "in progress", "completed"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Task(TaskBase):
    id: UUID


# Endpoints

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_create: TaskCreate):
    new_id = uuid4()
    task = Task(id=new_id, **task_create.model_dump())
    db_tasks.append(task)
    return task

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return db_tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID):
    for task in db_tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: UUID, task_update: TaskUpdate):
    for index, task in enumerate(db_tasks):
        if task.id == task_id:
            updated_task_data = task_update.model_dump(exclude_unset=True)
            db_tasks[index] = Task(**{**task.model_dump(), **updated_task_data})
            return db_tasks[index]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID):
    for index, task in enumerate(db_tasks):
        if task.id == task_id:
            db_tasks.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@app.get("/")
async def root():
    return {"message": "Hello World"}
