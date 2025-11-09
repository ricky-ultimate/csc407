from fastapi import APIRouter
from app.db import db
from app.schemas.course import CourseCreate, CourseOut

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/", response_model=CourseOut)
async def create_course(course: CourseCreate):
    return await db.course.create(data=course.dict()) # type: ignore

@router.get("/", response_model=list[CourseOut])
async def list_courses():
    return await db.course.find_many()
