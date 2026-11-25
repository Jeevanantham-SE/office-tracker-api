from typing import List, Optional
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import TaskModel, LeaveModel
from schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    LeaveCreate,
    LeaveResponse,
)
from auth import verify_api_key

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Office Leave & Task Tracker API",
    description="API for managing office tasks and employee leave requests",
    version="1.0.0",
)


@app.get("/")
def root():
    return FileResponse("static/index.html")  


# -------------------- TASKS ENDPOINTS --------------------


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    clean_title = task.title.strip()
    clean_assignee = task.assignee.strip()
    if not clean_title or not clean_assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and assignee cannot be blank whitespace",
        )

    new_task = TaskModel(
        title=clean_title,
        assignee=clean_assignee,
        done=task.done,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get(
    "/tasks",
    response_model=List[TaskResponse],
    dependencies=[Depends(verify_api_key)],
)
def list_tasks(
    done: Optional[bool] = None,
    assignee: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TaskModel)
    if done is not None:
        query = query.filter(TaskModel.done == done)
    if assignee:
        query = query.filter(TaskModel.assignee == assignee.strip())
    return query.all()


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(verify_api_key)],
)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if updates.title is not None:
        clean_title = updates.title.strip()
        if not clean_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be blank whitespace",
            )
        task.title = clean_title

    if updates.assignee is not None:
        clean_assignee = updates.assignee.strip()
        if not clean_assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee cannot be blank whitespace",
            )
        task.assignee = clean_assignee

    if updates.done is not None:
        task.done = updates.done

    db.commit()
    db.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    dependencies=[Depends(verify_api_key)],
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted successfully"}


# -------------------- LEAVES ENDPOINTS --------------------


@app.post(
    "/leaves",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
def apply_leave(leave: LeaveCreate, db: Session = Depends(get_db)):
    new_leave = LeaveModel(
        employee_name=leave.employee_name.strip(),
        start_date=leave.start_date.strip(),
        end_date=leave.end_date.strip(),
        reason=leave.reason.strip(),
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave


@app.get(
    "/leaves",
    response_model=List[LeaveResponse],
    dependencies=[Depends(verify_api_key)],
)
def list_leaves(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(LeaveModel)
    if status_filter:
        query = query.filter(LeaveModel.status == status_filter.strip())
    return query.all()


@app.patch(
    "/leaves/{leave_id}/approve",
    response_model=LeaveResponse,
    dependencies=[Depends(verify_api_key)],
)
def approve_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveModel).filter(LeaveModel.id == leave_id).first()
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )

    leave.status = "Approved"
    db.commit()
    db.refresh(leave)
    return leave
