"""
seed.py - Seed the database with sample data for testing
Run with: python seed.py
"""

from database import SessionLocal, init_db
from auth import hash_password
import models
from datetime import date, datetime, timedelta

def seed():
    init_db()
    db = SessionLocal()

    print("🌱 Seeding database...")

    # ── Users ──
    users_data = [
        {"username": "admin",       "email": "admin@health.com",      "role": models.UserRoleEnum.admin},
        {"username": "dr_sharma",   "email": "sharma@health.com",     "role": models.UserRoleEnum.doctor},
        {"username": "dr_priya",    "email": "priya@health.com",      "role": models.UserRoleEnum.doctor},
        {"username": "patient_raj", "email": "raj@example.com",       "role": models.UserRoleEnum.patient},
        {"username": "patient_anu", "email": "anu@example.com",       "role": models.UserRoleEnum.patient},
        {"username": "receptionist","email": "front@health.com",      "role": models.UserRoleEnum.receptionist},
        {"username": "pharmacist",  "email": "pharmacy@health.com",   "role": models.UserRoleEnum.pharmacist},
    ]
    users = {}
    for u in users_data:
        user = models.User(hashed_password=hash_password("Test@1234"), **u)
        db.add(user)
        db.flush()
        users[u["username"]] = user
    print("  ✅ Users created")

    # ── Departments ──
    depts_data = [
        {"name": "General Medicine",  "description": "Primary care and general consultations"},
        {"name": "Cardiology",        "description": "Heart and cardiovascular diseases"},
        {"name": "Orthopedics",       "description": "Bone, joint, and muscle conditions"},
        {"name": "Pediatrics",        "description": "Child healthcare"},
        {"name": "Pathology/Lab",     "description": "Laboratory and diagnostic services"},
    ]
    depts = {}
    for d in depts_data:
        dept = models.Department(**d)
        db.add(dept)
        db.flush()
        depts[d["name"]] = dept
    print("  ✅ Departments created")

    # ── Doctors ──
    doc1 = models.Doctor(
        user_id=users["dr_sharma"].id,
        department_id=depts["General Medicine"].id,
        first_name="Ravi", last_name="Sharma",
        specialization="General Physician",
        license_number="MH-DOC-001",
        phone="9876543210",
        consultation_fee=500.0,
        available_days="Mon,Tue,Wed,Thu,Fri"
    )
    doc2 = models.Doctor(
        user_id=users["dr_priya"].id,
        department_id=depts["Cardiology"].id,
        first_name="Priya", last_name="Nair",
        specialization="Cardiologist",
        license_number="MH-DOC-002",
        phone="9876543211",
        consultation_fee=1200.0,
        available_days="Mon,Wed,Fri"
    )
    db.add_all([doc1, doc2])
    db.flush()
    print("  ✅ Doctors created")

    # ── Patients ──
    pat1 = models.Patient(
        user_id=users["patient_raj"].id,
        first_name="Raj", last_name="Kumar",
        date_of_birth=date(1990, 5, 15),
        gender=models.GenderEnum.male,
        blood_group=models.BloodGroupEnum.B_pos,
        phone="9988776655",
        address="12 MG Road, Mysuru",
        emergency_contact="Sunita Kumar",
        emergency_phone="9988776644",
        allergies="Penicillin",
        insurance_provider="Star Health"
    )
    pat2 = models.Patient(
        user_id=users["patient_anu"].id,
        first_name="Anushka", last_name="Menon",
        date_of_birth=date(1985, 11, 20),
        gender=models.GenderEnum.female,
        blood_group=models.BloodGroupEnum.O_pos,
        phone="9900112233",
        address="45 Palace Road, Mysuru",
        emergency_contact="Vikram Menon",
        emergency_phone="9900112244",
    )
    db.add_all([pat1, pat2])
    db.flush()
    print("  ✅ Patients created")

    # ── Appointments ──
    appt1 = models.Appointment(
        patient_id=pat1.id, doctor_id=doc1.id,
        appointment_date=datetime.now() + timedelta(days=1),
        reason="Fever and cold for 3 days",
        status=models.AppointmentStatusEnum.scheduled
    )
    appt2 = models.Appointment(
        patient_id=pat2.id, doctor_id=doc2.id,
        appointment_date=datetime.now() - timedelta(days=2),
        reason="Chest pain checkup",
        status=models.AppointmentStatusEnum.completed
    )
    db.add_all([appt1, appt2])
    db.flush()
    print("  ✅ Appointments created")

    # ── Medical Record ──
    rec = models.MedicalRecord(
        patient_id=pat2.id, appointment_id=appt2.id,
        diagnosis="Mild hypertension",
        symptoms="Chest tightness, dizziness",
        treatment="Prescribed Amlodipine 5mg, lifestyle changes",
        notes="Patient advised to reduce salt intake",
        follow_up_date=date.today() + timedelta(days=30)
    )
    db.add(rec)
    db.flush()
    print("  ✅ Medical record created")

    # ── Prescription ──
    rx = models.Prescription(
        patient_id=pat2.id, doctor_id=doc2.id,
        medical_record_id=rec.id,
        medicine_name="Amlodipine 5mg",
        dosage="5mg",
        frequency="Once daily at night",
        duration_days=30,
        instructions="Take after dinner"
    )
    db.add(rx)
    db.flush()
    print("  ✅ Prescription created")

    # ── Lab Report ──
    lab = models.LabReport(
        patient_id=pat2.id, medical_record_id=rec.id,
        test_name="ECG",
        test_type="Cardiac",
        result="Normal sinus rhythm, no ST changes",
        is_abnormal=False,
        report_date=date.today(),
        lab_technician="Suresh Lab"
    )
    db.add(lab)
    db.flush()
    print("  ✅ Lab report created")

    # ── Inventory ──
    inv_items = [
        models.Inventory(item_name="Paracetamol 500mg", category="medicine", quantity=500, unit="tablets", unit_price=1.5, reorder_level=50),
        models.Inventory(item_name="Amlodipine 5mg",    category="medicine", quantity=200, unit="tablets", unit_price=4.0, reorder_level=30),
        models.Inventory(item_name="Surgical Gloves",   category="supply",   quantity=100, unit="pairs",   unit_price=12.0, reorder_level=20),
        models.Inventory(item_name="IV Drip 500ml",     category="supply",   quantity=8,   unit="bottles", unit_price=80.0, reorder_level=10),
    ]
    db.add_all(inv_items)
    db.flush()
    print("  ✅ Inventory seeded")

    # ── Billing ──
    import uuid
    bill = models.Billing(
        patient_id=pat2.id,
        appointment_id=appt2.id,
        invoice_number=f"INV-SEED-{str(uuid.uuid4())[:6].upper()}",
        consultation_fee=1200.0,
        medicine_charges=120.0,
        lab_charges=500.0,
        other_charges=0.0,
        discount=50.0,
        tax=5.0,
        total_amount=1861.0,
        paid_amount=1861.0,
        balance_due=0.0,
        payment_method="card",
        status=models.BillingStatusEnum.paid
    )
    db.add(bill)
    db.commit()
    print("  ✅ Billing seeded")

    print("\n🎉 Database seeded! Default password for all users: Test@1234")
    print("   Admin login: username=admin, password=Test@1234")

if __name__ == "__main__":
    seed()