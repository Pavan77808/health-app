from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, Enum, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"
    receptionist = "receptionist"
    pharmacist = "pharmacist"

class AppointmentStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"

class BillingStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    partial = "partial"
    cancelled = "cancelled"

class BloodGroupEnum(str, enum.Enum):
    A_pos = "A+"
    A_neg = "A-"
    B_pos = "B+"
    B_neg = "B-"
    AB_pos = "AB+"
    AB_neg = "AB-"
    O_pos = "O+"
    O_neg = "O-"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.patient)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    patient = relationship("Patient", back_populates="user", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    doctors = relationship("Doctor", back_populates="department")


class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    specialization = Column(String(100))
    license_number = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20))
    consultation_fee = Column(Float, default=0.0)
    available_days = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="doctor")
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum))
    blood_group = Column(Enum(BloodGroupEnum))
    phone = Column(String(20))
    address = Column(Text)
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    allergies = Column(Text)
    insurance_id = Column(String(50))
    insurance_provider = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    bills = relationship("Billing", back_populates="patient")
    lab_reports = relationship("LabReport", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text)
    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.scheduled)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False)
    bill = relationship("Billing", back_populates="appointment", uselist=False)


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    diagnosis = Column(Text, nullable=False)
    symptoms = Column(Text)
    treatment = Column(Text)
    notes = Column(Text)
    follow_up_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    patient = relationship("Patient", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_record")
    prescriptions = relationship("Prescription", back_populates="medical_record")
    lab_reports = relationship("LabReport", back_populates="medical_record")


class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"))
    medicine_name = Column(String(200), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration_days = Column(Integer)
    instructions = Column(Text)
    is_dispensed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    medical_record = relationship("MedicalRecord", back_populates="prescriptions")


class LabReport(Base):
    __tablename__ = "lab_reports"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"))
    test_name = Column(String(200), nullable=False)
    test_type = Column(String(100))
    result = Column(Text)
    reference_range = Column(String(200))
    is_abnormal = Column(Boolean, default=False)
    report_date = Column(Date)
    lab_technician = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    patient = relationship("Patient", back_populates="lab_reports")
    medical_record = relationship("MedicalRecord", back_populates="lab_reports")


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100))
    quantity = Column(Integer, default=0)
    unit = Column(String(50))
    unit_price = Column(Float, default=0.0)
    reorder_level = Column(Integer, default=10)
    expiry_date = Column(Date)
    supplier = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    billing_items = relationship("BillingItem", back_populates="inventory_item")


class Billing(Base):
    __tablename__ = "billing"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    invoice_number = Column(String(50), unique=True, nullable=False)
    consultation_fee = Column(Float, default=0.0)
    medicine_charges = Column(Float, default=0.0)
    lab_charges = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)
    payment_method = Column(String(50))
    status = Column(Enum(BillingStatusEnum), default=BillingStatusEnum.pending)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    patient = relationship("Patient", back_populates="bills")
    appointment = relationship("Appointment", back_populates="bill")
    billing_items = relationship("BillingItem", back_populates="bill")


class BillingItem(Base):
    __tablename__ = "billing_items"
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("billing.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    description = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    bill = relationship("Billing", back_populates="billing_items")
    inventory_item = relationship("Inventory", back_populates="billing_items")