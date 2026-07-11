from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .config import settings
from .routers import auth, courses, progress, payments, certificates, notifications, users, favorites
from .models import User, Course, Lesson
from .security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Astro Lab API", version="1.0.0")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(certificates.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")

@app.get("/")
def home():
    return {"status": "Astro Lab API is running"}

# Seed DB on startup if empty
@app.on_event("startup")
def seed_database():
    db = SessionLocal()
    try:
        # Check if users already exist
        user_count = db.query(User).count()
        if user_count == 0:
            print("Seeding database...")
            # Create users
            admin = User(
                name="Admin User",
                email="admin@astrolab.com",
                hashedPassword=get_password_hash("admin123"),
                role="ADMIN",
                totalXP=5000,
                streak=10
            )
            student = User(
                name="Mina Chen",
                email="student@astrolab.com",
                hashedPassword=get_password_hash("student123"),
                role="STUDENT",
                totalXP=8450,
                streak=14
            )
            db.add(admin)
            db.add(student)
            db.commit()

            # Create courses
            c1 = Course(
                id="c1",
                title="Quantum Mechanics: The Grand Tour",
                slug="quantum-mechanics-grand-tour",
                description="Build a deep, intuitive understanding of quantum mechanics through premium lessons, guided projects, and elegant visual explanations.",
                thumbnail="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=900&q=80",
                category="Physics",
                instructor="Dr. Elena Rostova",
                level="ADVANCED",
                duration=1110, # 18h 30m
                price=199.00,
                discount=20.0,
                isPublished=True,
                isPremium=True,
                isFeatured=True
            )
            c2 = Course(
                id="c2",
                title="Astrobiology Foundations",
                slug="astrobiology-foundations",
                description="Explore the origins of life on Earth and the search for biosignatures across the cosmos in this foundational astrobiology course.",
                thumbnail="https://images.unsplash.com/photo-1462332420958-a05d1e002413?auto=format&fit=crop&w=900&q=80",
                category="Astronomy",
                instructor="Prof. Marcus Chen",
                level="BEGINNER",
                duration=735, # 12h 15m
                price=149.00,
                discount=10.0,
                isPublished=True,
                isPremium=True,
                isFeatured=True
            )
            c3 = Course(
                id="c3",
                title="Deep Learning for Natural Sciences",
                slug="deep-learning-natural-sciences",
                description="Apply state-of-the-art neural architectures to physics models, bioinformatics, and chemistry data processing.",
                thumbnail="https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=900&q=80",
                category="AI",
                instructor="Dr. Sarah Jenkins",
                level="INTERMEDIATE",
                duration=1485, # 24h 45m
                price=249.00,
                discount=15.0,
                isPublished=True,
                isPremium=True,
                isFeatured=True
            )
            
            db.add_all([c1, c2, c3])
            db.commit()

            # Create lessons for c1
            l1 = Lesson(
                id="l1",
                title="Introduction to Wave-Particle Duality",
                description="Understand the foundational duality of matter and energy that governs the quantum world.",
                videoUrl="https://www.w3schools.com/html/mov_bbb.mp4",
                duration=480, # 8 mins
                position=1,
                isFree=True,
                courseId="c1"
            )
            l2 = Lesson(
                id="l2",
                title="The Schrodinger Equation Unpacked",
                description="Dive deep into the mathematics of wave functions and state probabilities.",
                videoUrl="https://www.w3schools.com/html/mov_bbb.mp4",
                duration=600, # 10 mins
                position=2,
                isFree=False,
                courseId="c1"
            )
            l3 = Lesson(
                id="l3",
                title="Quantum Superposition and the Measurement Problem",
                description="Analyze the physics of superposition and what happens during the observer collapse.",
                videoUrl="https://www.w3schools.com/html/mov_bbb.mp4",
                duration=1125, # 18h 45m (mocked in seconds as 1125s)
                position=3,
                isFree=False,
                courseId="c1"
            )
            
            # Create lessons for c2
            l4 = Lesson(
                id="l4",
                title="What is Life? A Cosmic Definition",
                description="Understand the thermodynamic definitions of living systems and planetary envelopes.",
                videoUrl="https://www.w3schools.com/html/mov_bbb.mp4",
                duration=540,
                position=1,
                isFree=True,
                courseId="c2"
            )
            
            db.add_all([l1, l2, l3, l4])
            db.commit()
            print("Database seeded successfully!")
            
    finally:
        db.close()
