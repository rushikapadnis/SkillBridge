from pydantic import BaseModel
from typing import Optional


class Signup(BaseModel):
    name: str
    email: str
    password: str
    role: str
    institution_id: Optional[int] = None


class Login(BaseModel):
    email: str
    password: str


class BatchCreate(BaseModel):
    name: str
    institution_id: int


class JoinBatch(BaseModel):
    token: str


class SessionCreate(BaseModel):
    title: str
    batch_id: int
    date: str
    start_time: str
    end_time: str


class AttendanceMark(BaseModel):
    session_id: int
    status: str