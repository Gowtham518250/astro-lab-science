# Astro Lab Backend — FastAPI + PostgreSQL

## Architecture

```
backend/
├── app/
│   ├── routers/          # HTTP route handlers (thin controllers)
│   │   ├── auth.py       ← Login / Register / Session
│   │   ├── courses.py    ← Course catalog & details
│   │   ├── progress.py   ← Lesson video progress
│   │   ├── payments.py   ← Course checkout & enrollment
│   │   ├── certificates.py ← Certificate listing
│   │   ├── notifications.py
│   │   ├── favorites.py  ← Bookmark toggle
│   │   └── users.py      ← Admin: user listing & stats
│   ├── services/         # Business logic layer
│   │   ├── auth_service.py
│   │   └── course_service.py
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # DB session management (PostgreSQL / SQLite fallback)
│   ├── security.py       # JWT + bcrypt
│   ├── config.py         # Environment variables
│   └── main.py           # FastAPI app, CORS, routers, seeder
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

The server starts at http://localhost:8000  
Interactive API docs: http://localhost:8000/docs  
Alternative docs: http://localhost:8000/redoc

## Deploy with Docker

```bash
docker build -t astrolab-backend .
docker run -p 8000:8000 --env-file .env astrolab-backend
```

## Deploy with Docker Compose (Full Stack)

From the project root:

```bash
docker-compose up --build
```

## Deploy to Railway / Render / Fly.io

1. Push this `backend/` folder as a separate repository (or connect monorepo)
2. Set environment variable `DATABASE_URL` to your PostgreSQL connection string
3. Set environment variable `JWT_SECRET_KEY` to a secure random string
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth` | Get current session user |
| POST | `/api/auth` | Login / Register / Logout |
| GET | `/api/courses` | List published courses |
| GET | `/api/courses/{id}` | Get course with lessons |
| GET | `/api/progress` | Get user enrollments |
| POST | `/api/progress` | Update lesson progress |
| POST | `/api/payment` | Checkout (enroll in course) |
| GET | `/api/certificates` | List user certificates |
| GET | `/api/favorites` | List saved courses |
| POST | `/api/favorites` | Toggle favorite |
| GET | `/api/notifications` | Get notifications |
| POST | `/api/notifications` | Mark read / create |
| GET | `/api/users` | Admin: list all users |
| GET | `/api/users/me` | Current user profile |
| GET | `/api/users/stats` | Admin: platform stats |

## Seed Data

On first startup, if the database is empty, the server automatically seeds:
- **Admin account**: `admin@astrolab.com` / `admin123`
- **Student account**: `student@astrolab.com` / `student123`
- **3 sample courses** with lessons
