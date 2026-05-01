SkillBridge Attendance System – Backend API (FastAPI)

Project Overview : 

This project is a role-based attendance management system built using:

FastAPI (backend framework)
SQLAlchemy (ORM)
PostgreSQL (Neon DB)
JWT authentication
Pydantic Validation 
Render Deployment 


👥 Supported Roles:
Student
Trainer
Institution
Programme Manager
Monitoring Officer


## 🚀 Live API

**Base URL:**

```
https://skillbridge-backend-4ali.onrender.com/docs#/
```

**Docs (Swagger UI):**

```
https://skillbridge-backend-4ali.onrender.com/
```

### Deployment Notes

* Deployed using **Render**
* Database hosted on **Neon (PostgreSQL)**
* Environment variables configured securely via platform settings
* SSL required for Neon DB connection

---

#  Local Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/rushikapadnis/SkillBridge.git
cd attendance-system
```

## 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Setup Environment Variables

Create `.env` file:

```env
DATABASE_URL= " " # it should be private so i  not past here 
SECRET_KEY=supersecret
ALGORITHM=HS256
MONITORING_API_KEY=myapikey
```

## 5. Run Server

```bash
uvicorn main:app --reload
```

## 6. Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

# 👥 Test Accounts

| Role               | Email                                               | Password |
| ------------------ | --------------------------------------------------- | -------- |
| Student            | [student@test.com](mailto:student@test.com)         | 123      |
| Trainer            | [trainer@test.com](mailto:trainer@test.com)         | 123      |
| Institution        | [institution@test.com](mailto:institution@test.com) | 123      |
| Programme Manager  | [pm@test.com](mailto:pm@test.com)                   | 123      |
| Monitoring Officer | [monitor@test.com](mailto:monitor@test.com)         | 123      |

---

#  Authentication Flow

## Step 1: Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"student@test.com","password":"123"}'
```

 Response:

```
{"token":"JWT_TOKEN"}
```

---

# 📡 API Endpoints (Sample cURL)

##  Signup

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
-H "Content-Type: application/json" \
-d '{"name":"test","email":"test@test.com","password":"123","role":"student"}'
```

---

##  Create Batch (Trainer)

```bash
curl -X POST http://127.0.0.1:8000/batches \
-H "Authorization: Bearer TOKEN" \
-H "Content-Type: application/json" \
-d '{"name":"Batch A","institution_id":1}'
```

---

##  Generate Invite

```bash
curl -X POST http://127.0.0.1:8000/batches/1/invite \
-H "Authorization: Bearer TOKEN"
```

---

##  Join Batch (Student)

```bash
curl -X POST http://127.0.0.1:8000/batches/join \
-H "Authorization: Bearer TOKEN" \
-d 'token=INVITE_TOKEN'
```

---

##  Create Session

```bash
curl -X POST http://127.0.0.1:8000/sessions \
-H "Authorization: Bearer TOKEN" \
-H "Content-Type: application/json" \
-d '{"title":"Session 1","batch_id":1}'
```

---

##  Mark Attendance

```bash
curl -X POST http://127.0.0.1:8000/attendance/mark \
-H "Authorization: Bearer TOKEN" \
-H "Content-Type: application/json" \
-d '{"session_id":1,"status":"present"}'
```

---

##  Session Attendance

```bash
curl -X GET http://127.0.0.1:8000/sessions/1/attendance \
-H "Authorization: Bearer TOKEN"
```

---

#  Monitoring Officer Token (Special Flow)

## Step 1: Login (normal JWT)

## Step 2: Get Monitoring Token

```bash
curl -X POST http://127.0.0.1:8000/auth/monitoring-token \
-H "Authorization: Bearer JWT_TOKEN" \
-d "key=myapikey"
```

---

## Step 3: Access Monitoring Endpoint

```bash
curl -X GET http://127.0.0.1:8000/monitoring/attendance \
-H "Authorization: Bearer MONITORING_TOKEN"
```

---

#  Schema Decisions

### 1. `batch_trainers`

* Implemented as a **many-to-many relationship**
* Allows multiple trainers per batch

### 2. `batch_invites`

* Token-based system for joining batches
* Includes:

  * unique token
  * `used` flag to prevent reuse

### 3. Dual Token System (Monitoring Officer)

* Normal JWT → login authentication
* Special short-lived token → monitoring access
* Improves security by limiting exposure

---

#  What’s Fully Working

* Authentication (Signup/Login)
* Role-Based Access Control (RBAC)
* Batch creation and joining
* Session creation
* Attendance marking
* Monitoring Officer token flow
* Basic API testing via Swagger

---

#  Partially Implemented

* Advanced validation (422 responses can be improved)
* Summary endpoints (basic version implemented)
* Seed script can be expanded

---

#  Skipped / Not Fully Implemented

* Full test coverage (only basic tests included)
* Pagination for large datasets
* Token revocation / refresh mechanism

---

#  What I’d Do With More Time

I would implement:

* **Token refresh + revocation system**
* **Advanced analytics dashboards**
* **Better validation and error handling**
* **Docker-based deployment for scalability**

---

# 📞 Contact

**Name:** Rushikesh Kapadnis
**Email:** [rushikapadnis09@gmail.com](mailto:rushikapadnis09@gmail.com)
**GitHub:** https://github.com/rushikapadnis

---


