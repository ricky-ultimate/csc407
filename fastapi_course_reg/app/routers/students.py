from fastapi import APIRouter, HTTPException
from app.db import db
from app.schemas.student import StudentCreate, StudentOut

def _transform_student(student):
    """Flatten the registration relationship into a list of courses."""
    courses = [r.course for r in student.registeredCourses] if student.registeredCourses else []
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "registeredCourses": courses
    }


router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentOut)
async def create_student(student: StudentCreate):
    existing = await db.student.find_unique(where={"email": student.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_student = await db.student.create(
        data=student.dict(),
        include={"registeredCourses": {"include": {"course": True}}}
    )
    return _transform_student(new_student)


@router.get("/", response_model=list[StudentOut])
async def list_students():
    students = await db.student.find_many(
        include={"registeredCourses": {"include": {"course": True}}}
    )
    return [_transform_student(s) for s in students]
