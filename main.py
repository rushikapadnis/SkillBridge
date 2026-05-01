from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid, random

from database import Base, engine, SessionLocal
from models import *
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


def hash_password(p): return pwd_context.hash(p)

def verify_password(p, h): return pwd_context.verify(p, h)

# ---------------- AUTH ----------------
@app.post("/auth/signup")
def signup(data: Signup, db: Session = Depends(get_db)):
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
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_token({"user_id": user.id, "role": user.role}, 24)}

# ---------------- BATCH ----------------
@app.post("/batches")
def create_batch(data: BatchCreate, db: Session = Depends(get_db), user=Depends(require_role(["trainer", "institution"]))):
    batch = Batch(name=data.name, institution_id=data.institution_id)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

@app.post("/batches/{batch_id}/invite")
def invite(batch_id: int, db: Session = Depends(get_db), user=Depends(require_role(["trainer"]))):
    token = str(uuid.uuid4())
    inv = BatchInvite(batch_id=batch_id, token=token, used=False, created_by=user["user_id"])
    db.add(inv)
    db.commit()
    return {"invite_token": token}

@app.post("/batches/join")
def join_batch(data: JoinBatch, db: Session = Depends(get_db), user=Depends(require_role(["student"]))):
    invite = db.query(BatchInvite).filter(BatchInvite.token == data.token, BatchInvite.used == False).first()
    if not invite or invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(400, "Invalid or expired invite")

    mapping = BatchStudent(batch_id=invite.batch_id, student_id=user["user_id"])
    invite.used = True

    db.add(mapping)
    db.commit()
    return {"message": "Joined batch successfully"}

# ---------------- SESSIONS ----------------
@app.post("/sessions")
def create_session(data: SessionCreate, db: Session = Depends(get_db), user=Depends(require_role(["trainer"]))):
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
    return session

@app.get("/sessions/{session_id}/attendance")
def get_attendance(session_id: int, db: Session = Depends(get_db), user=Depends(require_role(["trainer"]))):
    records = db.query(Attendance).filter(Attendance.session_id == session_id).all()
    return records

# ---------------- ATTENDANCE ----------------
@app.post("/attendance/mark")
def mark_attendance(data: AttendanceMark, db: Session = Depends(get_db), user=Depends(require_role(["student"]))):
    session = db.query(SessionModel).filter(SessionModel.id == data.session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")

    record = Attendance(
        session_id=data.session_id,
        student_id=user["user_id"],
        status=data.status,
        marked_at=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    return {"message": "Attendance marked"}

# ---------------- SUMMARY APIs ----------------
@app.get("/batches/{batch_id}/summary")
def batch_summary(batch_id: int, db: Session = Depends(get_db), user=Depends(require_role(["institution"]))):
    sessions = db.query(SessionModel).filter(SessionModel.batch_id == batch_id).all()
    return {"total_sessions": len(sessions)}

@app.get("/institutions/{inst_id}/summary")
def institution_summary(inst_id: int, db: Session = Depends(get_db), user=Depends(require_role(["programme_manager"]))):
    batches = db.query(Batch).filter(Batch.institution_id == inst_id).all()
    return {"total_batches": len(batches)}

@app.get("/programme/summary")
def programme_summary(db: Session = Depends(get_db), user=Depends(require_role(["programme_manager"]))):
    return {
        "total_users": db.query(User).count(),
        "total_batches": db.query(Batch).count(),
        "total_sessions": db.query(SessionModel).count()
    }

@app.get("/monitoring/attendance")
def monitoring(db: Session = Depends(get_db), user=Depends(require_role(["monitoring_officer"]))):
    return db.query(Attendance).all()

# ---------------- SEED SCRIPT ----------------
def seed():
    db = SessionLocal()

    inst1 = Institution(name="Inst A")
    inst2 = Institution(name="Inst B")

    db.add_all([inst1, inst2])
    db.commit()

    trainers = []
    students = []

    for i in range(4):
        t = User(name=f"Trainer{i}", email=f"t{i}@x.com", hashed_password=hash_password("123"), role="trainer", institution_id=inst1.id)
        trainers.append(t)

    for i in range(15):
        s = User(name=f"Student{i}", email=f"s{i}@x.com", hashed_password=hash_password("123"), role="student", institution_id=inst1.id)
        students.append(s)

    db.add_all(trainers + students)
    db.commit()

    batches = [Batch(name=f"Batch{i}", institution_id=inst1.id) for i in range(3)]
    db.add_all(batches)
    db.commit()

    for b in batches:
        for t in random.sample(trainers, 2):
            db.add(BatchTrainer(batch_id=b.id, trainer_id=t.id))

        for s in students[:5]:
            db.add(BatchStudent(batch_id=b.id, student_id=s.id))

    db.commit()

    sessions = []
    for i in range(8):
        sessions.append(SessionModel(
            batch_id=random.choice(batches).id,
            trainer_id=random.choice(trainers).id,
            title=f"Session {i}",
            date=datetime.utcnow().date(),
            start_time="10:00",
            end_time="11:00"
        ))

    db.add_all(sessions)
    db.commit()

    for s in sessions:
        for st in students[:5]:
            db.add(Attendance(session_id=s.id, student_id=st.id, status=random.choice(["present", "absent", "late"]), marked_at=datetime.utcnow()))

    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
