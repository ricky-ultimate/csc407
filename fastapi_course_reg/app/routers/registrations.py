from fastapi import APIRouter, HTTPException
from app.db import db
from app.schemas.registration import RegistrationCreate, RegistrationOut

router = APIRouter(prefix="/registrations", tags=["Registrations"])

@router.post("/", response_model=RegistrationOut)
async def register_student(data: RegistrationCreate):
    # Verify student and course exist
    student = await db.student.find_unique(where={"id": data.student_id})
    course = await db.course.find_unique(where={"id": data.course_id})
    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")

    # Prevent duplicates
    existing = await db.registration.find_first(
        where={"studentId": data.student_id, "courseId": data.course_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    # Create registration and include related data
    registration = await db.registration.create(
        data={"studentId": data.student_id, "courseId": data.course_id},
        include={"student": True, "course": True}
    )

    return registration
