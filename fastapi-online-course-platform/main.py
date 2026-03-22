from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(
    title="EduNest - Online Course Platform",
    description="A FastAPI-based online learning platform with courses, enrollments, and progress tracking.",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# In-Memory Data Store
# ─────────────────────────────────────────────

courses_db = {
    1: {"id": 1, "title": "Python for Beginners", "instructor": "Ananya Sharma", "category": "Programming", "price": 499.0, "duration_hours": 12, "rating": 4.8, "enrolled_count": 0, "available": True},
    2: {"id": 2, "title": "FastAPI Masterclass", "instructor": "Rahul Mehta", "category": "Web Development", "price": 799.0, "duration_hours": 8, "rating": 4.9, "enrolled_count": 0, "available": True},
    3: {"id": 3, "title": "Data Science with Pandas", "instructor": "Priya Nair", "category": "Data Science", "price": 999.0, "duration_hours": 20, "rating": 4.7, "enrolled_count": 0, "available": True},
    4: {"id": 4, "title": "React & TypeScript Bootcamp", "instructor": "Kiran Das", "category": "Web Development", "price": 1199.0, "duration_hours": 25, "rating": 4.6, "enrolled_count": 0, "available": True},
    5: {"id": 5, "title": "Machine Learning A-Z", "instructor": "Deepa Rao", "category": "AI/ML", "price": 1499.0, "duration_hours": 40, "rating": 4.9, "enrolled_count": 0, "available": True},
    6: {"id": 6, "title": "Docker & Kubernetes", "instructor": "Amit Joshi", "category": "DevOps", "price": 899.0, "duration_hours": 15, "rating": 4.5, "enrolled_count": 0, "available": False},
}

students_db = {
    101: {"id": 101, "name": "Sneha Patel", "email": "sneha@mail.com", "enrolled_courses": []},
    102: {"id": 102, "name": "Vikram Singh", "email": "vikram@mail.com", "enrolled_courses": []},
    103: {"id": 103, "name": "Meena Iyer", "email": "meena@mail.com", "enrolled_courses": []},
}

enrollments_db = {}  # enrollment_id -> enrollment record
progress_db = {}     # (student_id, course_id) -> progress percent

next_course_id = 7
next_student_id = 104
next_enrollment_id = 1

# ─────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100, description="Course title")
    instructor: str = Field(..., min_length=3, max_length=60)
    category: str = Field(..., min_length=2, max_length=40)
    price: float = Field(..., ge=0.0, le=50000.0, description="Price in INR")
    duration_hours: int = Field(..., ge=1, le=500)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    instructor: Optional[str] = Field(None, min_length=3, max_length=60)
    category: Optional[str] = Field(None, min_length=2, max_length=40)
    price: Optional[float] = Field(None, ge=0.0, le=50000.0)
    duration_hours: Optional[int] = Field(None, ge=1, le=500)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    available: Optional[bool] = None

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

class EnrollRequest(BaseModel):
    student_id: int = Field(..., ge=1)
    course_id: int = Field(..., ge=1)

class ProgressUpdate(BaseModel):
    student_id: int = Field(..., ge=1)
    course_id: int = Field(..., ge=1)
    percent: float = Field(..., ge=0.0, le=100.0, description="Completion percentage")

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def find_course(course_id: int):
    course = courses_db.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id {course_id} not found.")
    return course

def find_student(student_id: int):
    student = students_db.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found.")
    return student

def calculate_total_price(course_ids: list[int]) -> float:
    total = 0.0
    for cid in course_ids:
        course = courses_db.get(cid)
        if course:
            total += course["price"]
    return round(total, 2)

def filter_courses_logic(category=None, min_price=None, max_price=None, available_only=False):
    results = list(courses_db.values())
    if category is not None:
        results = [c for c in results if c["category"].lower() == category.lower()]
    if min_price is not None:
        results = [c for c in results if c["price"] >= min_price]
    if max_price is not None:
        results = [c for c in results if c["price"] <= max_price]
    if available_only:
        results = [c for c in results if c["available"]]
    return results

def paginate(items: list, page: int, size: int):
    total = len(items)
    total_pages = math.ceil(total / size) if size > 0 else 1
    start = (page - 1) * size
    end = start + size
    return {
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "items": items[start:end]
    }

# ─────────────────────────────────────────────
# Q1 — Home / Welcome Route
# ─────────────────────────────────────────────

@app.get("/", tags=["Home"])
def home():
    return {
        "platform": "EduNest 🎓",
        "message": "Welcome to EduNest – Learn Anything, Anywhere.",
        "total_courses": len(courses_db),
        "total_students": len(students_db),
        "docs": "/docs"
    }

# ─────────────────────────────────────────────
# Q2 — List All Courses
# ─────────────────────────────────────────────

@app.get("/courses", tags=["Courses"])
def get_all_courses():
    return {"total": len(courses_db), "courses": list(courses_db.values())}

# ─────────────────────────────────────────────
# Fixed route BEFORE variable route
# Q6 — Search (keyword search — Day 6)
# ─────────────────────────────────────────────

@app.get("/courses/search", tags=["Courses"])
def search_courses(
    keyword: str = Query(..., min_length=1, description="Search by title, instructor, or category"),
    sort_by: Optional[str] = Query(None, description="Sort by: price, rating, duration_hours"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=20)
):
    keyword_lower = keyword.lower()
    results = [
        c for c in courses_db.values()
        if keyword_lower in c["title"].lower()
        or keyword_lower in c["instructor"].lower()
        or keyword_lower in c["category"].lower()
    ]
    if sort_by is not None:
        if sort_by not in ("price", "rating", "duration_hours"):
            raise HTTPException(status_code=400, detail="sort_by must be: price, rating, duration_hours")
        results = sorted(results, key=lambda c: c[sort_by], reverse=(order == "desc"))
    return paginate(results, page, size)

# ─────────────────────────────────────────────
# Q7 — Summary / Count Endpoint
# ─────────────────────────────────────────────

@app.get("/courses/summary", tags=["Courses"])
def courses_summary():
    all_courses = list(courses_db.values())
    categories = {}
    for c in all_courses:
        categories[c["category"]] = categories.get(c["category"], 0) + 1
    avg_price = round(sum(c["price"] for c in all_courses) / len(all_courses), 2) if all_courses else 0
    avg_rating = round(sum(c["rating"] for c in all_courses) / len(all_courses), 2) if all_courses else 0
    return {
        "total_courses": len(all_courses),
        "available_courses": sum(1 for c in all_courses if c["available"]),
        "total_students": len(students_db),
        "total_enrollments": len(enrollments_db),
        "average_price_inr": avg_price,
        "average_rating": avg_rating,
        "courses_by_category": categories
    }

# ─────────────────────────────────────────────
# Q3 — Get Course by ID (variable route AFTER fixed)
# ─────────────────────────────────────────────

@app.get("/courses/{course_id}", tags=["Courses"])
def get_course_by_id(course_id: int = Path(..., ge=1)):
    return find_course(course_id)

# ─────────────────────────────────────────────
# Q4 — Create Course (POST + Pydantic)
# ─────────────────────────────────────────────

@app.post("/courses", status_code=201, tags=["Courses"])
def create_course(course: CourseCreate):
    global next_course_id
    new_course = {
        "id": next_course_id,
        "title": course.title,
        "instructor": course.instructor,
        "category": course.category,
        "price": course.price,
        "duration_hours": course.duration_hours,
        "rating": course.rating,
        "enrolled_count": 0,
        "available": True
    }
    courses_db[next_course_id] = new_course
    next_course_id += 1
    return {"message": "Course created successfully.", "course": new_course}

# ─────────────────────────────────────────────
# Q5 — Update Course (PUT)
# ─────────────────────────────────────────────

@app.put("/courses/{course_id}", tags=["Courses"])
def update_course(course_id: int, updates: CourseUpdate):
    course = find_course(course_id)
    update_data = updates.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    course.update(update_data)
    courses_db[course_id] = course
    return {"message": "Course updated successfully.", "course": course}

# ─────────────────────────────────────────────
# Q8 — Delete Course (DELETE)
# ─────────────────────────────────────────────

@app.delete("/courses/{course_id}", tags=["Courses"])
def delete_course(course_id: int):
    find_course(course_id)
    del courses_db[course_id]
    return {"message": f"Course {course_id} deleted successfully."}

# ─────────────────────────────────────────────
# Students — CRUD
# ─────────────────────────────────────────────

@app.get("/students", tags=["Students"])
def get_all_students():
    return {"total": len(students_db), "students": list(students_db.values())}

@app.get("/students/summary", tags=["Students"])
def students_summary():
    students = list(students_db.values())
    return {
        "total_students": len(students),
        "students_with_enrollments": sum(1 for s in students if s["enrolled_courses"]),
    }

@app.get("/students/{student_id}", tags=["Students"])
def get_student(student_id: int = Path(..., ge=1)):
    return find_student(student_id)

@app.post("/students", status_code=201, tags=["Students"])
def create_student(student: StudentCreate):
    global next_student_id
    # Duplicate email check
    for s in students_db.values():
        if s["email"] == student.email:
            raise HTTPException(status_code=400, detail="Student with this email already exists.")
    new_student = {
        "id": next_student_id,
        "name": student.name,
        "email": student.email,
        "enrolled_courses": []
    }
    students_db[next_student_id] = new_student
    next_student_id += 1
    return {"message": "Student registered successfully.", "student": new_student}

@app.delete("/students/{student_id}", tags=["Students"])
def delete_student(student_id: int):
    find_student(student_id)
    del students_db[student_id]
    return {"message": f"Student {student_id} removed."}

# ─────────────────────────────────────────────
# Q9 — Multi-Step Workflow: Enroll → Progress → Certificate
# Step 1: Enroll in a course
# ─────────────────────────────────────────────

@app.post("/enroll", status_code=201, tags=["Enrollment Workflow"])
def enroll_student(req: EnrollRequest):
    global next_enrollment_id
    student = find_student(req.student_id)
    course = find_course(req.course_id)

    if not course["available"]:
        raise HTTPException(status_code=400, detail="This course is not currently available for enrollment.")

    if req.course_id in student["enrolled_courses"]:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this course.")

    enrollment = {
        "enrollment_id": next_enrollment_id,
        "student_id": req.student_id,
        "course_id": req.course_id,
        "status": "enrolled"
    }
    enrollments_db[next_enrollment_id] = enrollment
    students_db[req.student_id]["enrolled_courses"].append(req.course_id)
    courses_db[req.course_id]["enrolled_count"] += 1
    progress_db[(req.student_id, req.course_id)] = 0.0
    next_enrollment_id += 1

    return {
        "message": f"✅ {student['name']} enrolled in '{course['title']}'.",
        "enrollment": enrollment
    }

# ─────────────────────────────────────────────
# Step 2: Update Progress
# ─────────────────────────────────────────────

@app.put("/progress", tags=["Enrollment Workflow"])
def update_progress(req: ProgressUpdate):
    find_student(req.student_id)
    find_course(req.course_id)

    key = (req.student_id, req.course_id)
    if key not in progress_db:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course.")

    progress_db[key] = req.percent
    status = "completed" if req.percent >= 100.0 else "in_progress"

    # Update enrollment status
    for enr in enrollments_db.values():
        if enr["student_id"] == req.student_id and enr["course_id"] == req.course_id:
            enr["status"] = status

    return {
        "message": f"Progress updated to {req.percent}%.",
        "student_id": req.student_id,
        "course_id": req.course_id,
        "progress_percent": req.percent,
        "status": status
    }

# ─────────────────────────────────────────────
# Step 3: Generate Certificate (only on 100%)
# ─────────────────────────────────────────────

@app.get("/certificate/{student_id}/{course_id}", tags=["Enrollment Workflow"])
def get_certificate(student_id: int, course_id: int):
    student = find_student(student_id)
    course = find_course(course_id)

    key = (student_id, course_id)
    if key not in progress_db:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course.")

    if progress_db[key] < 100.0:
        raise HTTPException(
            status_code=400,
            detail=f"Course not completed yet. Current progress: {progress_db[key]}%"
        )

    return {
        "🎓 Certificate of Completion": {
            "student_name": student["name"],
            "course_title": course["title"],
            "instructor": course["instructor"],
            "category": course["category"],
            "issued_by": "EduNest Platform",
            "status": "CERTIFIED ✅"
        }
    }

# ─────────────────────────────────────────────
# Q10 — Get Enrollments for a Student
# ─────────────────────────────────────────────

@app.get("/students/{student_id}/enrollments", tags=["Enrollment Workflow"])
def get_student_enrollments(student_id: int):
    find_student(student_id)
    enrolled = [
        {
            **enr,
            "course_title": courses_db[enr["course_id"]]["title"] if enr["course_id"] in courses_db else "Deleted",
            "progress_percent": progress_db.get((student_id, enr["course_id"]), 0.0)
        }
        for enr in enrollments_db.values()
        if enr["student_id"] == student_id
    ]
    total_price = calculate_total_price(
        [enr["course_id"] for enr in enrollments_db.values() if enr["student_id"] == student_id]
    )
    return {
        "student_id": student_id,
        "enrollments": enrolled,
        "total_courses_enrolled": len(enrolled),
        "total_amount_paid_inr": total_price
    }

# ─────────────────────────────────────────────
# Q11 — Advanced: Sort All Courses
# ─────────────────────────────────────────────

@app.get("/courses/sort/results", tags=["Advanced"])
def sort_courses(
    sort_by: str = Query("rating", description="Field to sort by: price, rating, duration_hours, enrolled_count"),
    order: str = Query("desc", description="asc or desc")
):
    valid_fields = ("price", "rating", "duration_hours", "enrolled_count")
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_fields}")
    reverse = (order == "desc")
    sorted_courses = sorted(courses_db.values(), key=lambda c: c[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "courses": sorted_courses}

# ─────────────────────────────────────────────
# Q12 — Advanced: Paginated Course List
# ─────────────────────────────────────────────

@app.get("/courses/page/list", tags=["Advanced"])
def paginated_courses(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(3, ge=1, le=20, description="Items per page")
):
    all_courses = list(courses_db.values())
    return paginate(all_courses, page, size)

# ─────────────────────────────────────────────
# Q19 — List All Enrollments (admin view)
# ─────────────────────────────────────────────

@app.get("/enrollments", tags=["Enrollment Workflow"])
def get_all_enrollments():
    enriched = []
    for enr in enrollments_db.values():
        student = students_db.get(enr["student_id"], {})
        course = courses_db.get(enr["course_id"], {})
        enriched.append({
            **enr,
            "student_name": student.get("name", "Unknown"),
            "course_title": course.get("title", "Deleted"),
            "progress_percent": progress_db.get((enr["student_id"], enr["course_id"]), 0.0)
        })
    return {"total_enrollments": len(enriched), "enrollments": enriched}

# ─────────────────────────────────────────────
# Q13 — Advanced: Combined Browse (filter + sort + paginate)
# ─────────────────────────────────────────────

@app.get("/courses/browse/all", tags=["Advanced"])
def browse_courses(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    available_only: bool = Query(False),
    sort_by: Optional[str] = Query(None, description="Sort by: price, rating, duration_hours"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=20)
):
    results = filter_courses_logic(category, min_price, max_price, available_only)
    if sort_by is not None:
        if sort_by not in ("price", "rating", "duration_hours"):
            raise HTTPException(status_code=400, detail="sort_by must be: price, rating, duration_hours")
        results = sorted(results, key=lambda c: c[sort_by], reverse=(order == "desc"))
    return paginate(results, page, size)

# ─────────────────────────────────────────────
# Q18 — Get All Students (with enrolled course count)
# ─────────────────────────────────────────────

@app.get("/students/list/all", tags=["Students"])
def list_all_students_detailed():
    result = []
    for s in students_db.values():
        result.append({
            **s,
            "total_enrolled": len(s["enrolled_courses"]),
            "total_spent_inr": calculate_total_price(s["enrolled_courses"])
        })
    return {"total": len(result), "students": result}

# ─────────────────────────────────────────────
# Q19 — Get Progress for a Student across all courses
# ─────────────────────────────────────────────

@app.get("/students/{student_id}/progress", tags=["Enrollment Workflow"])
def get_student_progress(student_id: int):
    find_student(student_id)
    progress_list = []
    for (sid, cid), percent in progress_db.items():
        if sid == student_id:
            course = courses_db.get(cid, {})
            progress_list.append({
                "course_id": cid,
                "course_title": course.get("title", "Deleted"),
                "progress_percent": percent,
                "status": "completed" if percent >= 100.0 else "in_progress"
            })
    completed = sum(1 for p in progress_list if p["status"] == "completed")
    return {
        "student_id": student_id,
        "total_courses": len(progress_list),
        "completed": completed,
        "in_progress": len(progress_list) - completed,
        "progress": progress_list
    }

# ─────────────────────────────────────────────
# Q20 — Filter Students by Enrollment Status
# ─────────────────────────────────────────────

@app.get("/students/filter/by-enrollment", tags=["Students"])
def filter_students_by_enrollment(
    enrolled: Optional[bool] = Query(None, description="True = has enrollments, False = no enrollments"),
    min_courses: int = Query(0, ge=0, description="Minimum number of enrolled courses"),
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=20)
):
    results = list(students_db.values())
    if enrolled is not None:
        if enrolled:
            results = [s for s in results if len(s["enrolled_courses"]) > 0]
        else:
            results = [s for s in results if len(s["enrolled_courses"]) == 0]
    if min_courses > 0:
        results = [s for s in results if len(s["enrolled_courses"]) >= min_courses]
    enriched = [
        {**s, "total_enrolled": len(s["enrolled_courses"])}
        for s in results
    ]
    return paginate(enriched, page, size)