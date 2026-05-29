"""
健康档案管理模块
记录和管理用户的健康数据
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.logger import logger


class VitalSigns(BaseModel):
    """生命体征"""
    temperature: Optional[float] = None  # 体温 (℃)
    heart_rate: Optional[int] = None     # 心率 (bpm)
    blood_pressure_sys: Optional[int] = None  # 收缩压 (mmHg)
    blood_pressure_dia: Optional[int] = None  # 舒张压 (mmHg)
    blood_sugar: Optional[float] = None  # 血糖 (mmol/L)
    weight: Optional[float] = None       # 体重 (kg)
    oxygen_saturation: Optional[int] = None  # 血氧 (%)
    recorded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SymptomRecord(BaseModel):
    """症状记录"""
    description: str
    location: Optional[str] = None     # 部位
    severity: Optional[str] = None     # 轻度/中度/重度
    duration: Optional[str] = None     # 持续时间
    triggers: list[str] = Field(default_factory=list)  # 诱因
    recorded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MedicationRecord(BaseModel):
    """用药记录"""
    drug_name: str
    dosage: Optional[str] = None       # 剂量
    frequency: Optional[str] = None    # 频率（每日一次/每日两次等）
    start_date: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HealthRecord(BaseModel):
    """用户健康档案"""
    user_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # 基本信息
    age: Optional[int] = None
    gender: Optional[str] = None
    allergies: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)

    # 健康数据
    vital_signs: list[VitalSigns] = Field(default_factory=list)
    symptoms: list[SymptomRecord] = Field(default_factory=list)
    medications: list[MedicationRecord] = Field(default_factory=list)

    def add_vital_signs(self, vitals: VitalSigns):
        self.vital_signs.append(vitals)
        self._touch()

    def add_symptom(self, symptom: SymptomRecord):
        self.symptoms.append(symptom)
        self._touch()

    def add_medication(self, medication: MedicationRecord):
        self.medications.append(medication)
        self._touch()

    def get_recent_vitals(self, count: int = 5) -> list[VitalSigns]:
        return self.vital_signs[-count:]

    def get_recent_symptoms(self, count: int = 5) -> list[SymptomRecord]:
        return self.symptoms[-count:]

    def get_current_medications(self) -> list[MedicationRecord]:
        """获取当前在用的药物"""
        return self.medications[-10:]

    def check_drug_allergy(self, drug_name: str) -> bool:
        """检查药物过敏"""
        return drug_name in self.allergies

    def get_summary(self) -> dict:
        """生成健康摘要"""
        return {
            "age": self.age,
            "gender": self.gender,
            "allergies": self.allergies,
            "chronic_conditions": self.chronic_conditions,
            "vital_signs_count": len(self.vital_signs),
            "symptoms_count": len(self.symptoms),
            "medications_count": len(self.medications),
            "last_updated": self.updated_at,
        }

    def _touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()


# 全局健康档案注册表（简化版，生产应使用数据库）
_health_records: dict[str, HealthRecord] = {}


def get_health_record(user_id: str) -> HealthRecord:
    """获取用户健康档案"""
    if user_id not in _health_records:
        _health_records[user_id] = HealthRecord(user_id=user_id)
        logger.info(f"创建用户健康档案: {user_id}")
    return _health_records[user_id]
