from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, Date, DateTime, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class ApplicationMethodEnum(enum.Enum):
    IM = "IM"
    SC = "SC"
    ORAL = "oral"
    OCULAR = "ocular"
    NASAL = "nasal"
    PUNCION = "puncion"
    AGUA = "agua"

class ImmunityStatusEnum(enum.Enum):
    PROTEGIDO = "protegido"
    PROTECCION_PARCIAL = "proteccion_parcial"
    DESARROLLO = "desarrollo"
    PENDIENTE = "pendiente"
    REFUERZO_NECESARIO = "refuerzo_necesario"

class AdverseReactionEnum(enum.Enum):
    NINGUNA = "ninguna"
    INFLAMACION_LEVE = "inflamacion_leve"
    FIEBRE = "fiebre"
    PERDIDA_APETITO = "perdida_apetito"
    LETARGO = "letargo"
    REACCION_LOCAL = "reaccion_local"
    OTRA = "otra"

class RecordStatusEnum(enum.Enum):
    APLICADA = "aplicada"
    PENDIENTE = "pendiente"
    CANCELADA = "cancelada"

class PriorityEnum(enum.Enum):
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"

class AlertTypeEnum(enum.Enum):
    PROXIMA = "proxima"
    VENCIDA = "vencida"
    URGENTE = "urgente"
    RECORDATORIO = "recordatorio"

class VaccineType(Base):
    __tablename__ = "vaccine_types"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    disease_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    application_method = Column(Enum(ApplicationMethodEnum), nullable=False)
    standard_dose = Column(String(20), nullable=True)
    protection_duration_days = Column(Integer, nullable=True)
    minimum_age_days = Column(Integer, nullable=True)
    is_mandatory = Column(Boolean, default=False)
    color_code = Column(String(7), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    vaccination_records = relationship("VaccinationRecord", back_populates="vaccine_type")
    schedules = relationship("VaccinationSchedule", back_populates="vaccine_type")
    alerts = relationship("VaccinationAlert", back_populates="vaccine_type")

class VaccinationRecord(Base):
    __tablename__ = "vaccination_records"
    
    id = Column(BigInteger, primary_key=True, index=True)
    rooster_id = Column(BigInteger, nullable=False, index=True)  # Por ahora sin FK hasta confirmar tabla gallos
    vaccine_type_id = Column(BigInteger, ForeignKey("vaccine_types.id"), nullable=False)
    application_date = Column(Date, nullable=False, index=True)
    veterinarian_name = Column(String(100), nullable=True)
    clinic_name = Column(String(100), nullable=True)
    medication_name = Column(String(150), nullable=True)
    dose_applied = Column(String(20), nullable=True)
    batch_number = Column(String(50), nullable=True)
    application_method = Column(Enum(ApplicationMethodEnum), nullable=False)
    rooster_weight_kg = Column(DECIMAL(5, 2), nullable=True)
    cost = Column(DECIMAL(10, 2), nullable=True)
    certificate_number = Column(String(100), nullable=True)
    next_dose_date = Column(Date, nullable=True)
    immunity_status = Column(Enum(ImmunityStatusEnum), nullable=True)
    adverse_reaction = Column(Enum(AdverseReactionEnum), default=AdverseReactionEnum.NINGUNA)
    observations = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)
    status = Column(Enum(RecordStatusEnum), default=RecordStatusEnum.APLICADA)
    user_id = Column(BigInteger, nullable=False)  # Por ahora sin FK hasta confirmar tabla users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    vaccine_type = relationship("VaccineType", back_populates="vaccination_records")
    schedules = relationship("VaccinationSchedule", back_populates="vaccination_record")

class VaccinationSchedule(Base):
    __tablename__ = "vaccination_schedules"
    
    id = Column(BigInteger, primary_key=True, index=True)
    rooster_id = Column(BigInteger, nullable=False, index=True)
    vaccine_type_id = Column(BigInteger, ForeignKey("vaccine_types.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False, index=True)
    is_reminder_sent = Column(Boolean, default=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.NORMAL)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    vaccination_record_id = Column(BigInteger, ForeignKey("vaccination_records.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    vaccine_type = relationship("VaccineType", back_populates="schedules")
    vaccination_record = relationship("VaccinationRecord", back_populates="schedules")
    
class VaccinationAlert(Base):
    __tablename__ = "vaccination_alerts"
    
    id = Column(BigInteger, primary_key=True, index=True)
    rooster_id = Column(BigInteger, nullable=False, index=True)
    vaccine_type_id = Column(BigInteger, ForeignKey("vaccine_types.id"), nullable=False)
    alert_type = Column(Enum(AlertTypeEnum), nullable=False, index=True)
    scheduled_date = Column(Date, nullable=False)
    days_remaining = Column(Integer, nullable=True)
    is_seen = Column(Boolean, default=False, index=True)
    is_dismissed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    vaccine_type = relationship("VaccineType", back_populates="alerts")