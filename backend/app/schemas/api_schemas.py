from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class DatasetResponse(BaseModel):
    id: int
    filename: str
    total_rows: int
    total_columns: int
    file_size_bytes: int
    data_quality_score: float
    status: str
    created_at: datetime
    summary_metrics: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    dataset_id: Optional[int]
    action: str
    module: str
    details: str
    timestamp: datetime

    class Config:
        from_attributes = True

class QualityScoreResponse(BaseModel):
    overall_score: float
    missing_penalty: float
    duplicate_penalty: float
    outlier_penalty: float
    validation_penalty: float
    explanation: str