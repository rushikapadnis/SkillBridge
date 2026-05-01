import traceback
print("MAIN STARTING")

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
import uuid, random

from database import Base, engine, SessionLocal

from models import (
    User,
    Batch,
    BatchStudent,
    BatchInvite,
    Session as SessionModel,
    Attendance,
    BatchTrainer
)

from schemas import *
from auth import create_token
from dependencies import require_role
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- DB SETUP ----------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(p):
    return pwd_context.hash(p)

def verify_password(p, h):
    return pwd_context.verify(p, h)

# ---------------- AUTH ----------------
@app.post("/auth/signup")
def signup(data: Signup, db: DBSession = Depends(get_db)):
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        institution_id=data.institution_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"token": create_token({"user_id": user.id, "role": user.role}, 24)}

@app.post("/auth/login")
def login(data: Login, db: DBSession = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    return {"token": create_token({"user_id": user.id, "role": user.role}, 24)}

# ---------------- BATCH ----------------
@app.post("/batches")
def create_batch(
    data: BatchCreate,
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["trainer", "institution"]))
):
    batch = Batch(name=data.name, institution_id=data.institution_id)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

@app.post("/batches/{batch_id}/invite")
def invite(
    batch_id: int,
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["trainer"]))
):
    token = str(uuid.uuid4())

    inv = BatchInvite(
        batch_id=batch_id,
        token=token,
        used=False,
        created_by=user["user_id"]
    )

    db.add(inv)
    db.commit()

    return {"invite_token": token}

@app.post("/batches/join")
def join_batch(
    data: JoinBatch,
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["student"]))
):
    invite = db.query(BatchInvite).filter(
        BatchInvite.token == data.token,
        BatchInvite.used == False
    ).first()

    if not invite:
        raise HTTPException(400, "Invalid invite")

    db.add(BatchStudent(
        batch_id=invite.batch_id,
        student_id=user["user_id"]
    ))

    invite.used = True
    db.commit()

    return {"message": "Joined batch successfully"}

# ---------------- SESSIONS ----------------
@app.post("/sessions")
def create_session(
    data: SessionCreate,
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["trainer"]))
):
    session = SessionModel(
        batch_id=data.batch_id,
        trainer_id=user["user_id"],
        title=data.title,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session

@app.get("/sessions/{session_id}/attendance")
def get_attendance(
    session_id: int,
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["trainer"]))
):
    return db.query(Attendance).filter(
        Attendance.session_id == session_id
    ).all()

# ---------------- ATTENDANCE ----------------
@app.post("/attendance/mark")
def mark_attendance(
    data: AttendanceMark,
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["student"]))
):
    session = db.query(SessionModel).filter(
        SessionModel.id == data.session_id
    ).first()

    if not session:
        raise HTTPException(404, "Session not found")

    db.add(Attendance(
        session_id=data.session_id,
        student_id=user["user_id"],
        status=data.status,
        marked_at=datetime.utcnow()
    ))

    db.commit()

    return {"message": "Attendance marked"}

# ---------------- SUMMARY ----------------
@app.get("/programme/summary")
def programme_summary(
    db: DBSession = Depends(get_db),
    user=Depends(require_role(["programme_manager"]))
):
    return {
        "total_users": db.query(User).count(),
        "total_batches": db.query(Batch).count(),
        "total_sessions": db.query(SessionModel).count()
    }

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "ok"}