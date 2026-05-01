from fastapi import FastAPI, Depends, HTTPException
from database import Base, engine, SessionLocal
from models import *
from schemas import *
from auth import create_token
from dependencies import require_role, get_current_user
from passlib.context import CryptContext
import os, uuid

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(p): return pwd_context.hash(p)

def verify_password(p, h): return pwd_context.verify(p, h)

# ---------- AUTH ----------
@app.post("/auth/signup")
def signup(data: Signup, db=Depends(get_db)):
    user = User(name=data.name, email=data.email, hashed_password=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    return {"token": create_token({"user_id": user.id, "role": user.role}, 24)}

@app.post("/auth/login")
def login(data: Login, db=Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token({"user_id": user.id, "role": user.role}, 24)}

# ---------- BATCH ----------
@app.post("/batches")
def create_batch(data: BatchCreate, db=Depends(get_db), user=Depends(require_role(["trainer","institution"]))):
    batch = Batch(name=data.name, institution_id=data.institution_id)
    db.add(batch)
    db.commit()
    return batch

@app.post("/batches/{id}/invite")
def invite(id:int, db=Depends(get_db), user=Depends(require_role(["trainer"]))):
    token = str(uuid.uuid4())
    inv = BatchInvite(batch_id=id, token=token, used=False)
    db.add(inv)
    db.commit()
    return {"invite_token": token}

@app.get("/")
def root():
    return {"message": "SkillBridge API is live "}

