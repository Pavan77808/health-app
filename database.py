from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import os

MYSQL_USER = "root"
MYSQL_PASS = quote_plus("970Alpha@123")
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB   = "health_app_db"

DATABASE_URL = (
    "mysql+pymysql://" + MYSQL_USER + ":" + MYSQL_PASS +
    "@" + MYSQL_HOST + ":" + MYSQL_PORT + "/" + MYSQL_DB
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import (
        User, Patient, Doctor, Appointment,
        MedicalRecord, Prescription, Billing,
        Department, Inventory, LabReport
    )
    Base.metadata.create_all(bind=engine)
    print("MySQL Database initialized successfully.")