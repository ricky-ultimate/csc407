from pydantic import BaseModel
from datetime import datetime
from app.schemas.student import StudentOut
from app.schemas.course import CourseOut

class RegistrationCreate(BaseModel):
    student_id: int
    course_id: int

class RegistrationOut(BaseModel):
    id: int
    studentId: int
    courseId: int
    registeredAt: datetime
    student: StudentOut | None = None
    course: CourseOut | None = None

    model_config = {
        "from_attributes": True
    }
