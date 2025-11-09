from fastapi import FastAPI
from app.db import connect_db, disconnect_db
from app.routers import students, courses, registrations

app = FastAPI(title="Course Registration API")

app.include_router(students.router)
app.include_router(courses.router)
app.include_router(registrations.router)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()
