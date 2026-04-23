"""
main.py - FastAPI application entry point
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import (
    auth_router, dept_router, doctor_router, patient_router,
    appointment_router, records_router, prescription_router,
    lab_router, inventory_router, billing_router,
    dashboard_router, report_router
)

app = FastAPI(
    title="Health Application API",
    description="Complete Health Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dept_router)
app.include_router(doctor_router)
app.include_router(patient_router)
app.include_router(appointment_router)
app.include_router(records_router)
app.include_router(prescription_router)
app.include_router(lab_router)
app.include_router(inventory_router)
app.include_router(billing_router)
app.include_router(report_router)

@app.on_event("startup")
def startup_event():
    init_db()
    print("Health Application API is running!")

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Health Application API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)