#  EduNest – Online Course Platform

A FastAPI project implementing a full-featured online learning platform with courses, student management, enrollment workflows, and advanced browsing.

---

##  Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload

# 3. Open Swagger UI
http://127.0.0.1:8000/docs
```

---

## 📁 Project Structure

```
fastapi_course_platform/
├── main.py            # All routes, models, helpers
├── requirements.txt   # Dependencies
├── README.md          # This file
└── screenshots/       # Swagger UI screenshots (Q1–Q20)
```

---

## 🗂 API Overview

### Home
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Welcome + platform stats (Q1) |

### Courses (CRUD)
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/courses` | List all courses (Q2) |
| GET | `/courses/search` | Keyword search (Q6) |
| GET | `/courses/summary` | Count & stats (Q7) |
| GET | `/courses/{id}` | Get course by ID (Q3) |
| POST | `/courses` | Create course (Q4) |
| PUT | `/courses/{id}` | Update course (Q5) |
| DELETE | `/courses/{id}` | Delete course (Q8) |

### Students
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/students` | List all students |
| GET | `/students/summary` | Student stats |
| GET | `/students/{id}` | Get student by ID |
| POST | `/students` | Register student |
| DELETE | `/students/{id}` | Remove student |

### Multi-Step Workflow (Day 5)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/enroll` | Step 1: Enroll student in course (Q9) |
| PUT | `/progress` | Step 2: Update progress % |
| GET | `/certificate/{sid}/{cid}` | Step 3: Issue certificate on 100% |
| GET | `/students/{id}/enrollments` | View all enrollments + total paid |

### Advanced (Day 6)
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/courses/sort/results` | Sort courses |
| GET | `/courses/page/list` | Paginated course list |
| GET | `/courses/browse/all` | Combined filter + sort + paginate (Q20) |

---

##  Key Concepts Implemented

### Route Order Rule (FastAPI)
Fixed routes always appear **before** variable routes:
```python
#  Correct order
@app.get("/courses/search")   # fixed – comes first
@app.get("/courses/summary")  # fixed – comes first
@app.get("/courses/{id}")     # variable – comes last
```

### Pydantic Validation
- `Field(min_length=..., max_length=..., ge=..., le=...)` constraints
- Email regex pattern validation
- Optional fields for partial updates (PUT)

### Helper Functions
| Function | Purpose |
|----------|---------|
| `find_course(id)` | Lookup or raise 404 |
| `find_student(id)` | Lookup or raise 404 |
| `calculate_total_price(ids)` | Sum prices for enrolled courses |
| `filter_courses_logic(...)` | Category/price/availability filter |
| `paginate(items, page, size)` | Generic pagination |

### Multi-Step Workflow
```
POST /enroll  →  PUT /progress  →  GET /certificate/{sid}/{cid}
```

### HTTP Status Codes
- `201 Created` – POST endpoints
- `404 Not Found` – Invalid IDs
- `400 Bad Request` – Business logic violations

---

## 📸 Screenshots

All Swagger UI tests are saved in `screenshots/`:

```
Q1_home_route.png
Q2_get_all_courses.png
Q3_get_course_by_id.png
Q4_create_course.png
Q5_update_course.png
Q6_search_courses.png
Q7_courses_summary.png
Q8_delete_course.png
Q9_enroll_student.png
Q10_update_progress.png
Q11_get_certificate.png
Q12_student_enrollments.png
Q13_sort_courses.png
Q14_paginated_courses.png
Q15_combined_browse.png
...
```

---

##  Tech Stack
- **Python 3.11+**
- **FastAPI 0.115**
- **Pydantic v2**
- **Uvicorn**
