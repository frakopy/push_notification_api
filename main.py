
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException # Unused reasearch how to use it
from fastapi.responses import HTMLResponse
from sqlite_mgmt import get_due_tasks, update_record, insert_record, get_task_list, delete_record, get_task

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class TaskSchema(BaseModel):
    id: int
    message: str
    frequency: str
    next_run: str  # SQLite handle dates as strings
    status: str
    topic: str

class TaskCreate(BaseModel):
    message: str
    frequency: str
    next_run: str
    time: str
    status: str
    topic: str

class TaskUpdate(BaseModel):
    message: Optional[str] = None
    frequency: Optional[str] = None
    next_run: Optional[str] = None
    status: Optional[str] = None
    topic: Optional[str] = None


@app.get("/tasks", response_model=list[TaskSchema])
def get_tasks():
    tasks = get_due_tasks()
    return tasks

@app.get("/tasks/list", response_class=HTMLResponse)
def get_full_tasks(request: Request):
    tasks = get_task_list()
    return templates.TemplateResponse(
        request=request, 
        name="task_list.html",
        context={"tasks":tasks}
        )


@app.get("/tasks/update/form", response_class=HTMLResponse)
def update_form(task_id: int, request: Request):
    task_fields = get_task(task_id)[0]
    
    return templates.TemplateResponse(
        request=request, 
        name="task_update.html",
        context={"task_fields": task_fields, "task_id": task_id}
    )


@app.post("/tasks/create")
def create_task(new_task : TaskCreate):
    new_task_dict = new_task.model_dump()
    new_task_dict["next_run"] = f"{new_task_dict['next_run']}T{new_task_dict['time']}"
    new_task_dict.pop("time")
    result = insert_record(**new_task_dict)
    if result:
        return {"result": "Record successfuly created"}
    else:
        return {"result": "Something went wrong, record not created"}


@app.delete("/tasks/delete/{task_id}")
def delete_task(task_id):
    result = delete_record(task_id)
    if result:
        return {"result": "Task successfully deleted"}
    else:
        return {"result": "Sorry, something went wrong"}


@app.put("/tasks/update/{task_id}")
def update_tasks(task_id: int, task_data : TaskUpdate):
    data_dict = task_data.model_dump()
    data_dict = {key: value for key, value in data_dict.items() if value is not None}
    if not data_dict:
        return {"result": "No data to update"}
    success = update_record(task_id, **data_dict)

    if success:
        return {"result": "Record successfuly updated"}
    else:
        return {"result": "Something went wrong, record couldn't be updated"}


@app.post("/tasks/delete/response", response_class=HTMLResponse)
def send_delete_response(request: Request):
    return templates.TemplateResponse(request=request, name="delete_response.html")


@app.get("/tasks/update/response", response_class=HTMLResponse)
def send_update_response(request: Request):
    return templates.TemplateResponse(request=request, name="update.response.html")
