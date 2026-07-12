import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .config import settings
from .routers import auth, courses, progress, payments, certificates, notifications, users, favorites, quiz, lessons, categories, instructors, reviews, coupons, payment_provider, platform, enterprise
from .models import User, Course, Lesson, Quiz, QuizQuestion
from .security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Astro Lab API", version="1.0.0")

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS middleware for local development and deployed frontends
configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
allow_origins = [origin.strip() for origin in configured_origins if origin.strip()]
allow_origin_regex = os.getenv(
    "CORS_ORIGIN_REGEX",
    r"https://.*\\.vercel\\.app|https://.*\\.netlify\\.app|https://.*\\.github\\.dev"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
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
app.include_router(quiz.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(instructors.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(coupons.router, prefix="/api")
app.include_router(payment_provider.router, prefix="/api")
app.include_router(platform.router, prefix="/api")
app.include_router(enterprise.router, prefix="/api")

@app.get("/")
def home():
    return {"status": "Astro Lab API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Seed DB on startup if empty
@app.on_event("startup")
def seed_database():
    print("Starting up...")
    db = SessionLocal()
    try:
        # Check if users already exist
        user_count = db.query(User).count()
        print(f"User count in DB: {user_count}")
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

            # Seed a Quiz for Course 1 (Quantum Mechanics)
            q1 = Quiz(
                id="quiz_c1",
                courseId="c1",
                title="Quantum Mechanics Fundamentals"
            )
            db.add(q1)
            db.commit()

            qq1 = QuizQuestion(
                id="qq1",
                quizId="quiz_c1",
                text="In the context of the double-slit experiment, what does observing the electron do to its superposition state?",
                options=["It duplicates the electron", "It forces the electron into a definite state (collapses the wave function)", "It reverses the electron's spin", "It has absolutely no effect on the electron"],
                answer=1
            )
            qq2 = QuizQuestion(
                id="qq2",
                quizId="quiz_c1",
                text="Which equation describes how the quantum state of a physical system changes in time?",
                options=["Maxwell's Equations", "Schrodinger Equation", "Einstein Field Equations", "Planck's Law"],
                answer=1
            )
            db.add_all([qq1, qq2])
            db.commit()

            print("Database seeded successfully!")
    except Exception as e:
        print(f"Error during database seeding: {e}")
        db.close()

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
    print("Startup complete!")
