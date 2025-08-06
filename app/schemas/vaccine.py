from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class ApplicationMethodEnum(str, Enum):
    IM = "IM"
    SC = "SC"
    ORAL = "oral"
    OCULAR = "ocular"
    NASAL = "nasal"
    PUNCION = "puncion"
    AGUA = "agua"

class ImmunityStatusEnum(str, Enum):
    PROTEGIDO = "protegido"
    PROTECCION_PARCIAL = "proteccion_parcial"
    DESARROLLO = "desarrollo"
    PENDIENTE = "pendiente"
    REFUERZO_NECESARIO = "refuerzo_necesario"

class AdverseReactionEnum(str, Enum):
    NINGUNA = "ninguna"
    INFLAMACION_LEVE = "inflamacion_leve"
    FIEBRE = "fiebre"
    PERDIDA_APETITO = "perdida_apetito"
    LETARGO = "letargo"
    REACCION_LOCAL = "reaccion_local"
    OTRA = "otra"

class RecordStatusEnum(str, Enum):
    APLICADA = "aplicada"
    PENDIENTE = "pendiente"
    CANCELADA = "cancelada"

class PriorityEnum(str, Enum):
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"

class AlertTypeEnum(str, Enum):
    PROXIMA = "proxima"
    VENCIDA = "vencida"
    URGENTE = "urgente"
    RECORDATORIO = "recordatorio"

class VaccineTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    disease_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    application_method: ApplicationMethodEnum
    standard_dose: Optional[str] = Field(None, max_length=20)
    protection_duration_days: Optional[int] = Field(None, gt=0)
    minimum_age_days: Optional[int] = Field(None, ge=0)
    is_mandatory: bool = False
    color_code: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    is_active: bool = True

class VaccineTypeCreate(VaccineTypeBase):
    pass

class VaccineTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    disease_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    application_method: Optional[ApplicationMethodEnum] = None
    standard_dose: Optional[str] = Field(None, max_length=20)
    protection_duration_days: Optional[int] = Field(None, gt=0)
    minimum_age_days: Optional[int] = Field(None, ge=0)
    is_mandatory: Optional[bool] = None
    color_code: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None

class VaccineTypeResponse(VaccineTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class VaccinationRecordBase(BaseModel):
    rooster_id: int
    vaccine_type_id: int
    application_date: date
    veterinarian_name: Optional[str] = Field(None, max_length=100)
    clinic_name: Optional[str] = Field(None, max_length=100)
    medication_name: Optional[str] = Field(None, max_length=150)
    dose_applied: Optional[str] = Field(None, max_length=20)
    batch_number: Optional[str] = Field(None, max_length=50)
    application_method: ApplicationMethodEnum
    rooster_weight_kg: Optional[Decimal] = Field(None, ge=0, le=999.99)
    cost: Optional[Decimal] = Field(None, ge=0)
    certificate_number: Optional[str] = Field(None, max_length=100)
    next_dose_date: Optional[date] = None
    immunity_status: Optional[ImmunityStatusEnum] = None
    adverse_reaction: AdverseReactionEnum = AdverseReactionEnum.NINGUNA
    observations: Optional[str] = None
    tags: Optional[str] = Field(None, max_length=255)
    status: RecordStatusEnum = RecordStatusEnum.APLICADA

class VaccinationRecordCreate(VaccinationRecordBase):
    pass

class VaccinationRecordQuick(BaseModel):
    rooster_ids: List[int] = Field(..., min_items=1)
    vaccine_type_ids: List[int] = Field(..., min_items=1)
    application_date: date

class VaccinationRecordUpdate(BaseModel):
    immunity_status: Optional[ImmunityStatusEnum] = None
    adverse_reaction: Optional[AdverseReactionEnum] = None
    observations: Optional[str] = None
    next_dose_date: Optional[date] = None
    status: Optional[RecordStatusEnum] = None

class VaccinationRecordResponse(VaccinationRecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    vaccine_type: Optional[VaccineTypeResponse] = None
    
    class Config:
        orm_mode = True

class VaccinationScheduleBase(BaseModel):
    rooster_id: int
    vaccine_type_id: int
    scheduled_date: date
    priority: PriorityEnum = PriorityEnum.NORMAL
    notes: Optional[str] = None
    
    @validator('scheduled_date')
    def validate_future_date(cls, v):
        if v < date.today():
            raise ValueError('La fecha programada debe ser futura')
        return v

class VaccinationScheduleCreate(VaccinationScheduleBase):
    pass

class VaccinationScheduleComplete(BaseModel):
    vaccination_record_id: int

class VaccinationScheduleResponse(VaccinationScheduleBase):
    id: int
    is_reminder_sent: bool
    is_completed: bool
    completed_at: Optional[datetime] = None
    vaccination_record_id: Optional[int] = None
    created_at: datetime
    vaccine_type: Optional[VaccineTypeResponse] = None
    days_remaining: Optional[int] = None
    is_overdue: bool = False
    
    class Config:
        orm_mode = True

class VaccinationAlertResponse(BaseModel):
    id: int
    rooster_id: int
    vaccine_type_id: int
    alert_type: AlertTypeEnum
    scheduled_date: date
    days_remaining: Optional[int] = None
    is_seen: bool
    is_dismissed: bool
    created_at: datetime
    vaccine_type: Optional[VaccineTypeResponse] = None
    
    class Config:
        orm_mode = True

class VaccinationStatistics(BaseModel):
    total_vaccinations: int
    vaccines_by_type: dict
    monthly_trend: List[dict]
    total_cost: Decimal
    average_cost_per_vaccine: Decimal
    protection_status: dict

class ComplianceReport(BaseModel):
    overall_compliance: float
    mandatory_vaccines_compliance: float
    optional_vaccines_compliance: float
    roosters_summary: List[dict]
    upcoming_due: int
    overdue_count: int

class CostReport(BaseModel):
    total_period_cost: Decimal
    average_monthly_cost: Decimal
    cost_by_vaccine_type: dict
    cost_by_veterinarian: dict
    projected_annual_cost: Decimal