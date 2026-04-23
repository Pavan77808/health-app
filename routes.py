from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from reports.generator import (
    generate_registration_report,
    generate_bill_report,
    generate_prescription_report,
    generate_lab_report
)
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
import uuid
from database import get_db
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_role
)
import models, schemas
from models import UserRoleEnum, BillingStatusEnum, AppointmentStatusEnum

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@auth_router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}

@auth_router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@auth_router.patch("/deactivate/{user_id}")
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(UserRoleEnum.admin))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.username} deactivated"}


dept_router = APIRouter(prefix="/departments", tags=["Departments"])

@dept_router.post("/", response_model=schemas.DepartmentResponse, status_code=201)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db), _: models.User = Depends(require_role(UserRoleEnum.admin))):
    existing = db.query(models.Department).filter(models.Department.name == dept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")
    d = models.Department(**dept.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

@dept_router.get("/", response_model=List[schemas.DepartmentResponse])
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Department).all()

@dept_router.get("/{dept_id}", response_model=schemas.DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


doctor_router = APIRouter(prefix="/doctors", tags=["Doctors"])

@doctor_router.post("/", response_model=schemas.DoctorResponse, status_code=201)
def register_doctor(doctor_data: schemas.DoctorCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin))):
    if db.query(models.Doctor).filter(models.Doctor.license_number == doctor_data.license_number).first():
        raise HTTPException(status_code=400, detail="License number already registered")
    doctor = models.Doctor(**doctor_data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@doctor_router.get("/", response_model=List[schemas.DoctorResponse])
def list_doctors(specialization: Optional[str] = None, department_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Doctor)
    if specialization:
        q = q.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    if department_id:
        q = q.filter(models.Doctor.department_id == department_id)
    return q.all()

@doctor_router.get("/{doctor_id}", response_model=schemas.DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


patient_router = APIRouter(prefix="/patients", tags=["Patients"])

@patient_router.post("/", response_model=schemas.PatientResponse, status_code=201)
def register_patient(patient_data: schemas.PatientCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(models.Patient).filter(models.Patient.user_id == patient_data.user_id).first():
        raise HTTPException(status_code=400, detail="Patient profile already exists")
    patient = models.Patient(**patient_data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@patient_router.get("/", response_model=List[schemas.PatientResponse])
def list_patients(search: Optional[str] = Query(None), skip: int = 0, limit: int = 20, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin, UserRoleEnum.doctor, UserRoleEnum.receptionist))):
    q = db.query(models.Patient)
    if search:
        q = q.filter(
            models.Patient.first_name.ilike(f"%{search}%") |
            models.Patient.last_name.ilike(f"%{search}%") |
            models.Patient.phone.ilike(f"%{search}%")
        )
    return q.offset(skip).limit(limit).all()

@patient_router.get("/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@patient_router.patch("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(patient_id: int, update_data: schemas.PatientUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


appointment_router = APIRouter(prefix="/appointments", tags=["Appointments"])

@appointment_router.post("/", response_model=schemas.AppointmentResponse, status_code=201)
def book_appointment(appt_data: schemas.AppointmentCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not db.query(models.Patient).filter(models.Patient.id == appt_data.patient_id).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    if not db.query(models.Doctor).filter(models.Doctor.id == appt_data.doctor_id).first():
        raise HTTPException(status_code=404, detail="Doctor not found")
    appt = models.Appointment(**appt_data.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt

@appointment_router.get("/", response_model=List[schemas.AppointmentResponse])
def list_appointments(patient_id: Optional[int] = None, doctor_id: Optional[int] = None, status: Optional[AppointmentStatusEnum] = None, from_date: Optional[date] = None, to_date: Optional[date] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Appointment)
    if patient_id: q = q.filter(models.Appointment.patient_id == patient_id)
    if doctor_id: q = q.filter(models.Appointment.doctor_id == doctor_id)
    if status: q = q.filter(models.Appointment.status == status)
    if from_date: q = q.filter(models.Appointment.appointment_date >= from_date)
    if to_date: q = q.filter(models.Appointment.appointment_date <= to_date)
    return q.order_by(models.Appointment.appointment_date).all()

@appointment_router.get("/{appt_id}", response_model=schemas.AppointmentResponse)
def get_appointment(appt_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    appt = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt

@appointment_router.patch("/{appt_id}", response_model=schemas.AppointmentResponse)
def update_appointment(appt_id: int, update_data: schemas.AppointmentUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    appt = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    return appt

@appointment_router.delete("/{appt_id}", status_code=204)
def cancel_appointment(appt_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    appt = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatusEnum.cancelled
    db.commit()


records_router = APIRouter(prefix="/medical-records", tags=["Medical Records"])

@records_router.post("/", response_model=schemas.MedicalRecordResponse, status_code=201)
def create_record(record_data: schemas.MedicalRecordCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.doctor, UserRoleEnum.admin))):
    record = models.MedicalRecord(**record_data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@records_router.get("/patient/{patient_id}", response_model=List[schemas.MedicalRecordResponse])
def get_patient_records(patient_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.patient_id == patient_id).order_by(models.MedicalRecord.created_at.desc()).all()

@records_router.get("/{record_id}", response_model=schemas.MedicalRecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


prescription_router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

@prescription_router.post("/", response_model=schemas.PrescriptionResponse, status_code=201)
def create_prescription(rx_data: schemas.PrescriptionCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.doctor, UserRoleEnum.admin))):
    rx = models.Prescription(**rx_data.model_dump())
    db.add(rx)
    db.commit()
    db.refresh(rx)
    return rx

@prescription_router.get("/patient/{patient_id}", response_model=List[schemas.PrescriptionResponse])
def get_patient_prescriptions(patient_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Prescription).filter(models.Prescription.patient_id == patient_id).order_by(models.Prescription.created_at.desc()).all()

@prescription_router.patch("/{rx_id}/dispense")
def dispense_prescription(rx_id: int, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.pharmacist, UserRoleEnum.admin))):
    rx = db.query(models.Prescription).filter(models.Prescription.id == rx_id).first()
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")
    rx.is_dispensed = True
    db.commit()
    return {"message": f"Prescription {rx_id} marked as dispensed"}


lab_router = APIRouter(prefix="/lab-reports", tags=["Lab Reports"])

@lab_router.post("/", response_model=schemas.LabReportResponse, status_code=201)
def create_lab_report(report_data: schemas.LabReportCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = models.LabReport(**report_data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@lab_router.get("/patient/{patient_id}", response_model=List[schemas.LabReportResponse])
def get_patient_lab_reports(patient_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.LabReport).filter(models.LabReport.patient_id == patient_id).order_by(models.LabReport.created_at.desc()).all()

@lab_router.get("/{report_id}", response_model=schemas.LabReportResponse)
def get_lab_report(report_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = db.query(models.LabReport).filter(models.LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    return report


inventory_router = APIRouter(prefix="/inventory", tags=["Inventory"])

@inventory_router.post("/", response_model=schemas.InventoryResponse, status_code=201)
def add_inventory_item(item_data: schemas.InventoryCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin, UserRoleEnum.pharmacist))):
    item = models.Inventory(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@inventory_router.get("/", response_model=List[schemas.InventoryResponse])
def list_inventory(category: Optional[str] = None, low_stock: bool = False, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Inventory)
    if category:
        q = q.filter(models.Inventory.category.ilike(f"%{category}%"))
    if low_stock:
        q = q.filter(models.Inventory.quantity <= models.Inventory.reorder_level)
    return q.all()

@inventory_router.patch("/{item_id}", response_model=schemas.InventoryResponse)
def update_inventory(item_id: int, update_data: schemas.InventoryUpdate, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin, UserRoleEnum.pharmacist))):
    item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@inventory_router.get("/alerts/low-stock", response_model=List[schemas.InventoryResponse])
def low_stock_alerts(db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin, UserRoleEnum.pharmacist))):
    return db.query(models.Inventory).filter(models.Inventory.quantity <= models.Inventory.reorder_level).all()


billing_router = APIRouter(prefix="/billing", tags=["Billing"])

def generate_invoice_number() -> str:
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

@billing_router.post("/", response_model=schemas.BillingResponse, status_code=201)
def create_bill(bill_data: schemas.BillingCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin, UserRoleEnum.receptionist))):
    subtotal = (bill_data.consultation_fee + bill_data.medicine_charges + bill_data.lab_charges + bill_data.other_charges)
    tax_amount = subtotal * (bill_data.tax / 100)
    total = subtotal + tax_amount - bill_data.discount
    bill = models.Billing(
        patient_id=bill_data.patient_id,
        appointment_id=bill_data.appointment_id,
        invoice_number=generate_invoice_number(),
        consultation_fee=bill_data.consultation_fee,
        medicine_charges=bill_data.medicine_charges,
        lab_charges=bill_data.lab_charges,
        other_charges=bill_data.other_charges,
        discount=bill_data.discount,
        tax=bill_data.tax,
        total_amount=round(total, 2),
        paid_amount=0.0,
        balance_due=round(total, 2),
        payment_method=bill_data.payment_method,
        notes=bill_data.notes
    )
    db.add(bill)
    db.flush()
    for item_data in bill_data.items:
        item_total = item_data.quantity * item_data.unit_price
        item = models.BillingItem(
            bill_id=bill.id,
            inventory_id=item_data.inventory_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=round(item_total, 2)
        )
        db.add(item)
        if item_data.inventory_id:
            inv = db.query(models.Inventory).filter(models.Inventory.id == item_data.inventory_id).first()
            if inv:
                inv.quantity = max(0, inv.quantity - item_data.quantity)
    db.commit()
    db.refresh(bill)
    return bill

@billing_router.get("/", response_model=List[schemas.BillingResponse])
def list_bills(patient_id: Optional[int] = None, status: Optional[BillingStatusEnum] = None, from_date: Optional[date] = None, to_date: Optional[date] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Billing)
    if patient_id: q = q.filter(models.Billing.patient_id == patient_id)
    if status: q = q.filter(models.Billing.status == status)
    if from_date: q = q.filter(models.Billing.created_at >= from_date)
    if to_date: q = q.filter(models.Billing.created_at <= to_date)
    return q.order_by(models.Billing.created_at.desc()).all()

@billing_router.get("/{bill_id}", response_model=schemas.BillingResponse)
def get_bill(bill_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    bill = db.query(models.Billing).filter(models.Billing.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@billing_router.post("/{bill_id}/payment", response_model=schemas.BillingResponse)
def process_payment(bill_id: int, payment: schemas.BillingPayment, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin, UserRoleEnum.receptionist))):
    bill = db.query(models.Billing).filter(models.Billing.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if bill.status == BillingStatusEnum.cancelled:
        raise HTTPException(status_code=400, detail="Cannot pay a cancelled bill")
    bill.paid_amount += payment.paid_amount
    bill.balance_due = round(bill.total_amount - bill.paid_amount, 2)
    bill.payment_method = payment.payment_method
    if bill.balance_due <= 0:
        bill.status = BillingStatusEnum.paid
        bill.balance_due = 0
    elif bill.paid_amount > 0:
        bill.status = BillingStatusEnum.partial
    db.commit()
    db.refresh(bill)
    return bill

@billing_router.patch("/{bill_id}/cancel")
def cancel_bill(bill_id: int, db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin))):
    bill = db.query(models.Billing).filter(models.Billing.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill.status = BillingStatusEnum.cancelled
    db.commit()
    return {"message": f"Bill {bill.invoice_number} cancelled"}


dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@dashboard_router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), _=Depends(require_role(UserRoleEnum.admin))):
    today = date.today()
    total_patients = db.query(func.count(models.Patient.id)).scalar()
    total_doctors = db.query(func.count(models.Doctor.id)).scalar()
    total_departments = db.query(func.count(models.Department.id)).scalar()
    today_appointments = db.query(func.count(models.Appointment.id)).filter(func.date(models.Appointment.appointment_date) == today).scalar()
    pending_bills = db.query(func.count(models.Billing.id)).filter(models.Billing.status == BillingStatusEnum.pending).scalar()
    total_revenue = db.query(func.sum(models.Billing.paid_amount)).filter(models.Billing.status == BillingStatusEnum.paid).scalar() or 0.0
    low_stock_items = db.query(func.count(models.Inventory.id)).filter(models.Inventory.quantity <= models.Inventory.reorder_level).scalar()
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_departments": total_departments,
        "today_appointments": today_appointments,
        "pending_bills": pending_bills,
        "total_revenue_collected": round(total_revenue, 2),
        "low_stock_alerts": low_stock_items,
        "generated_at": datetime.now().isoformat()
    }
# ═══════════════════════════════════════════════════════════════
# MODULE 12: REPORT GENERATION
# ═══════════════════════════════════════════════════════════════

report_router = APIRouter(prefix="/reports", tags=["📄 Reports"])

@report_router.get("/registration/{patient_id}")
def get_registration_report(
    patient_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor = None
    appt = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).first()
    if appt:
        doctor = db.query(models.Doctor).filter(
            models.Doctor.id == appt.doctor_id
        ).first()

    patient_dict = {
        "id":                patient.id,
        "first_name":        patient.first_name,
        "last_name":         patient.last_name,
        "date_of_birth":     str(patient.date_of_birth),
        "gender":            patient.gender.value if patient.gender else "-",
        "blood_group":       patient.blood_group.value if patient.blood_group else "-",
        "phone":             patient.phone,
        "address":           patient.address,
        "allergies":         patient.allergies,
        "emergency_contact": patient.emergency_contact,
        "emergency_phone":   patient.emergency_phone,
        "insurance_provider":patient.insurance_provider,
        "insurance_id":      patient.insurance_id,
    }

    doctor_dict = None
    if doctor:
        doctor_dict = {
            "first_name":       doctor.first_name,
            "last_name":        doctor.last_name,
            "specialization":   doctor.specialization,
            "license_number":   doctor.license_number,
            "consultation_fee": doctor.consultation_fee,
        }

    filepath = generate_registration_report(patient_dict, doctor_dict)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath)
    )


@report_router.get("/bill/{bill_id}")
def get_bill_report(
    bill_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    bill = db.query(models.Billing).filter(
        models.Billing.id == bill_id
    ).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    patient = db.query(models.Patient).filter(
        models.Patient.id == bill.patient_id
    ).first()

    bill_dict = {
        "invoice_number":   bill.invoice_number,
        "consultation_fee": bill.consultation_fee,
        "medicine_charges": bill.medicine_charges,
        "lab_charges":      bill.lab_charges,
        "other_charges":    bill.other_charges,
        "discount":         bill.discount,
        "tax":              bill.tax,
        "total_amount":     bill.total_amount,
        "paid_amount":      bill.paid_amount,
        "balance_due":      bill.balance_due,
        "payment_method":   bill.payment_method,
        "status":           bill.status.value if bill.status else "-",
    }

    patient_dict = {
        "id":         patient.id,
        "first_name": patient.first_name,
        "last_name":  patient.last_name,
        "phone":      patient.phone,
        "blood_group":patient.blood_group.value if patient.blood_group else "-",
    } if patient else {}

    filepath = generate_bill_report(bill_dict, patient_dict)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath)
    )


@report_router.get("/prescription/{patient_id}")
def get_prescription_report(
    patient_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.patient_id == patient_id
    ).all()

    doctor = None
    if prescriptions:
        doctor = db.query(models.Doctor).filter(
            models.Doctor.id == prescriptions[0].doctor_id
        ).first()

    rx_list = [{
        "medicine_name": rx.medicine_name,
        "dosage":        rx.dosage,
        "frequency":     rx.frequency,
        "duration_days": rx.duration_days,
        "instructions":  rx.instructions,
    } for rx in prescriptions]

    patient_dict = {
        "id":          patient.id,
        "first_name":  patient.first_name,
        "last_name":   patient.last_name,
        "phone":       patient.phone,
        "blood_group": patient.blood_group.value if patient.blood_group else "-",
    }

    doctor_dict = {
        "first_name":     doctor.first_name     if doctor else "-",
        "last_name":      doctor.last_name      if doctor else "-",
        "specialization": doctor.specialization if doctor else "-",
        "license_number": doctor.license_number if doctor else "-",
    }

    filepath = generate_prescription_report(rx_list, patient_dict, doctor_dict)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath)
    )


@report_router.get("/lab/{patient_id}")
def get_lab_report(
    patient_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    labs = db.query(models.LabReport).filter(
        models.LabReport.patient_id == patient_id
    ).all()

    lab_list = [{
        "test_name":       lab.test_name,
        "test_type":       lab.test_type,
        "result":          lab.result,
        "reference_range": lab.reference_range,
        "is_abnormal":     lab.is_abnormal,
        "report_date":     str(lab.report_date),
    } for lab in labs]

    patient_dict = {
        "id":          patient.id,
        "first_name":  patient.first_name,
        "last_name":   patient.last_name,
        "phone":       patient.phone,
        "blood_group": patient.blood_group.value if patient.blood_group else "-",
        "gender":      patient.gender.value if patient.gender else "-",
    }

    filepath = generate_lab_report(lab_list, patient_dict)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath)
    )