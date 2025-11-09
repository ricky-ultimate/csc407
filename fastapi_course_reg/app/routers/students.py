from fastapi import APIRouter, HTTPException
from app.db import db
from app.schemas.student import StudentCreate, StudentOut

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentOut)
async def create_student(student: StudentCreate):
    existing = await db.student.find_unique(where={"email": student.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_student = await db.student.create(data=student.dict())
    return new_student

@router.get("/", response_model=list[StudentOut])
async def list_students():
    return await db.student.find_many()
