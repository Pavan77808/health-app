from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from models import (
    GenderEnum, UserRoleEnum, AppointmentStatusEnum,
    BillingStatusEnum, BloodGroupEnum
)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRoleEnum = UserRoleEnum.patient

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRoleEnum
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PatientCreate(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: GenderEnum
    blood_group: Optional[BloodGroupEnum] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    allergies: Optional[str] = None
    insurance_id: Optional[str] = None
    insurance_provider: Optional[str] = None

class PatientUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    allergies: Optional[str] = None
    insurance_id: Optional[str] = None
    insurance_provider: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: GenderEnum
    blood_group: Optional[BloodGroupEnum]
    phone: Optional[str]
    address: Optional[str]
    insurance_provider: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DoctorCreate(BaseModel):
    user_id: int
    department_id: int
    first_name: str
    last_name: str
    specialization: str
    license_number: str
    phone: Optional[str] = None
    consultation_fee: float = 0.0
    available_days: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    user_id: int
    department_id: Optional[int]
    first_name: str
    last_name: str
    specialization: Optional[str]
    license_number: str
    consultation_fee: float
    available_days: Optional[str]
    class Config:
        from_attributes = True

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str]
    status: AppointmentStatusEnum
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class MedicalRecordCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    diagnosis: str
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None

class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    appointment_id: Optional[int]
    diagnosis: str
    symptoms: Optional[str]
    treatment: Optional[str]
    follow_up_date: Optional[date]
    created_at: datetime
    class Config:
        from_attributes = True

class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    medical_record_id: Optional[int] = None
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    instructions: Optional[str] = None

class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    medical_record_id: Optional[int]
    medicine_name: str
    dosage: Optional[str]
    frequency: Optional[str]
    duration_days: Optional[int]
    is_dispensed: bool
    created_at: datetime
    class Config:
        from_attributes = True

class LabReportCreate(BaseModel):
    patient_id: int
    medical_record_id: Optional[int] = None
    test_name: str
    test_type: Optional[str] = None
    result: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: bool = False
    report_date: Optional[date] = None
    lab_technician: Optional[str] = None
    notes: Optional[str] = None

class LabReportResponse(BaseModel):
    id: int
    patient_id: int
    test_name: str
    test_type: Optional[str]
    result: Optional[str]
    is_abnormal: bool
    report_date: Optional[date]
    created_at: datetime
    class Config:
        from_attributes = True

class InventoryCreate(BaseModel):
    item_name: str
    category: str
    quantity: int = 0
    unit: Optional[str] = None
    unit_price: float = 0.0
    reorder_level: int = 10
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    reorder_level: Optional[int] = None

class InventoryResponse(BaseModel):
    id: int
    item_name: str
    category: str
    quantity: int
    unit: Optional[str]
    unit_price: float
    reorder_level: int
    expiry_date: Optional[date]
    class Config:
        from_attributes = True

class BillingItemCreate(BaseModel):
    inventory_id: Optional[int] = None
    description: str
    quantity: int = 1
    unit_price: float

class BillingCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    consultation_fee: float = 0.0
    medicine_charges: float = 0.0
    lab_charges: float = 0.0
    other_charges: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    items: List[BillingItemCreate] = []

class BillingPayment(BaseModel):
    paid_amount: float
    payment_method: str

class BillingResponse(BaseModel):
    id: int
    patient_id: int
    appointment_id: Optional[int]
    invoice_number: str
    consultation_fee: float
    medicine_charges: float
    lab_charges: float
    other_charges: float
    discount: float
    tax: float
    total_amount: float
    paid_amount: float
    balance_due: float
    payment_method: Optional[str]
    status: BillingStatusEnum
    created_at: datetime
    class Config:
        from_attributes = True