# Course Registration API

## **1. `.env`**

```env
DATABASE_URL="postgresql://course_admin:yourpassword@localhost:5432/courses_db"
PORT=3000
```

* This file **stores secret or configurable values** for your app (like your database username/password).
* `DATABASE_URL` tells your app **how to connect to your PostgreSQL database**.
* `PORT` tells your app **what port to run on** (like the door to your app; 3000 is a common default).

Think of `.env` as a **config box** you don’t want to share publicly.

---

## **2. Launching the Server**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

* This command **starts the FastAPI server**.
* `uvicorn app.main:app`:

  * `uvicorn` → the ASGI server.
  * `app.main:app` → locate `app` inside `app/main.py`.
* `--host 0.0.0.0` → allows access from other devices on the same network.
* `--port 3000` → designates the port the server will run on.

---

## **3. `app/db.py`**

```python
from prisma import Prisma

db = Prisma()

async def connect_db():
    await db.connect()

async def disconnect_db():
    await db.disconnect()
```

* `db = Prisma()` → this is your **database client**. You use `db` to talk to the database.
* `connect_db()` → opens a connection to the database.
* `disconnect_db()` → closes the connection when your app stops.
* `async` means these **functions run in the background without freezing your app**.

---

## **4. `app/main.py`**

```python
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
```

* `FastAPI()` → creates your API app.
* `include_router` → lets you **divide routes into separate files** (students, courses, registrations).
* `@app.on_event("startup")` → **runs when your app starts**. Here, it connects to the database.
* `@app.on_event("shutdown")` → **runs when your app stops**. Here, it disconnects from the database.

This file is like the **main engine** of your app.

---

## **5. Routers**

Routers are **like controllers** in other frameworks—they handle API endpoints.

### **5a. `app/routers/students.py`**

```python
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
```

* `@router.post("/")` → **endpoint for creating a student**.
* `db.student.find_unique` → checks if a student already exists.
* `db.student.create` → adds a new student to the database.
* `_transform_student` → converts database format into a neat **JSON format** for API response.

```python
@router.get("/", response_model=list[StudentOut])
async def list_students():
    students = await db.student.find_many(
        include={"registeredCourses": {"include": {"course": True}}}
    )
    return [_transform_student(s) for s in students]
```

* `@router.get("/")` → **endpoint to list all students**.
* `db.student.find_many()` → fetches all students including their courses.

---

### **5b. `app/routers/courses.py`**

```python
@router.post("/", response_model=CourseOut)
async def create_course(course: CourseCreate):
    return await db.course.create(data=course.dict())
```

* Adds a **new course** to the database.

```python
@router.get("/", response_model=list[CourseOut])
async def list_courses():
    return await db.course.find_many()
```

* Lists **all courses**.

---

### **5c. `app/routers/registrations.py`**

```python
@router.post("/", response_model=RegistrationOut)
async def register_student(data: RegistrationCreate):
    student = await db.student.find_unique(where={"id": data.student_id})
    course = await db.course.find_unique(where={"id": data.course_id})
    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")

    existing = await db.registration.find_first(
        where={"studentId": data.student_id, "courseId": data.course_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    registration = await db.registration.create(
        data={"studentId": data.student_id, "courseId": data.course_id},
        include={"student": True, "course": True}
    )

    return registration
```

* Registers a **student for a course**.
* Checks **if student and course exist**, prevents duplicates, and **saves registration**.

---

## **6. Schemas**

Schemas define **the shape of data** (like rules for what a student, course, or registration looks like).

### Example: `app/schemas/student.py`

```python
class StudentCreate(BaseModel):
    name: str
    email: EmailStr

class StudentOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    registeredCourses: list[CourseOut] | None = None
```

* `StudentCreate` → data required when creating a student.
* `StudentOut` → data returned to the user, including registered courses.
* `EmailStr` → validates emails automatically.

---

## **7. Prisma schema (`prisma/schema.prisma`)**

```prisma
model Student {
    id                Int            @id @default(autoincrement())
    name              String
    email             String         @unique
    registeredCourses Registration[]
}
```

* Defines **database tables**.
* `@id` → primary key.
* `@default(autoincrement())` → automatically gives each new row a unique ID.
* `@unique` → ensures emails/codes are unique.
* `Registration[]` → a **relation table** to track which courses a student registered for.

---

## **8. Prisma Relevance**

* Prisma is the **database ORM (Object-Relational Mapper)**.
* Provides a **Python client (`prisma-client-py`)** to easily read/write database records.
* Ensures **type safety**: your database fields map to Python objects.
* Handles **relations automatically**, so we can fetch a student with their courses or a course with its registrations in one call.
* Eliminates boilerplate SQL: we write Python, Prisma generates queries.

Think of Prisma as **the bridge between the Python app and PostgreSQL**, managing data in a structured and type-safe way.

---

### **Summary of How It Works**

1. `.env` → store config like DB URL.
2. Launch server with `uvicorn`.
3. `db.py` → connects/disconnects database using Prisma.
4. `main.py` → central app, includes routers.
5. Routers → handle API requests (`students`, `courses`, `registrations`).
6. Schemas → validate and structure API input/output.
7. Prisma → defines database models and relationships and provides a type-safe client to interact with the DB.

Essentially, this is a **basic course registration API**: we can add students, add courses, and register students to courses, with Prisma handling all database interactions efficiently.
