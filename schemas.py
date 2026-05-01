from pydantic import BaseModel

class Signup(BaseModel):
    name: str
    email: str
    password: str
    role: str

class Login(BaseModel):
    email: str
    password: str

class BatchCreate(BaseModel):
    name: str
    institution_id: int

class SessionCreate(BaseModel):
    title: str
    batch_id: int

class AttendanceCreate(BaseModel):
    session_id: int
    status: str