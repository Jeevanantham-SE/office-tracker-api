from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    assignee: str = Field(..., min_length=1, max_length=80)
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    assignee: Optional[str] = Field(default=None, min_length=1, max_length=80)
    done: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    assignee: str
    done: bool

    model_config = ConfigDict(from_attributes=True)


class LeaveCreate(BaseModel):
    employee_name: str = Field(..., min_length=1, max_length=80)
    start_date: str = Field(..., min_length=8, max_length=20)
    end_date: str = Field(..., min_length=8, max_length=20)
    reason: str = Field(..., min_length=1, max_length=250)


class LeaveResponse(BaseModel):
    id: int
    employee_name: str
    start_date: str
    end_date: str
    reason: str
    status: str

    model_config = ConfigDict(from_attributes=True)
