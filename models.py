from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    institution_id = Column(Integer, nullable=True)

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    institution_id = Column(Integer)

class BatchStudent(Base):
    __tablename__ = "batch_students"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer)
    student_id = Column(Integer)

class BatchInvite(Base):
    __tablename__ = "batch_invites"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer)
    token = Column(String)
    used = Column(Boolean, default=False)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer)
    trainer_id = Column(Integer)
    title = Column(String)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer)
    student_id = Column(Integer)
    status = Column(String)