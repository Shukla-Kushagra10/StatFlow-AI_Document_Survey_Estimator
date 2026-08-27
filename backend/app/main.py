from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Relative imports within app package
from .config import settings
from .database import engine, Base, SessionLocal
from .models.schema_models import AuditLog
from .routes import upload, profile, clean, outliers, validate, weighting, estimation, insights, audit, reports

# Initialize all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="MoSPI AI-Enhanced Survey Data Cleaning, Estimation, and Reporting Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Complete Route Set
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(profile.router, prefix=settings.API_V1_STR)
app.include_router(clean.router, prefix=settings.API_V1_STR)
app.include_router(outliers.router, prefix=settings.API_V1_STR)
app.include_router(validate.router, prefix=settings.API_V1_STR)
app.include_router(weighting.router, prefix=settings.API_V1_STR)
app.include_router(estimation.router, prefix=settings.API_V1_STR)
app.include_router(insights.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        init_log = AuditLog(
            action="SYSTEM_INIT",
            module="CORE",
            details="All MoSPI Backend Services, Routes, and Database Engines initialized.",
            timestamp=datetime.utcnow()
        )
        db.add(init_log)
        db.commit()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "endpoints_docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }