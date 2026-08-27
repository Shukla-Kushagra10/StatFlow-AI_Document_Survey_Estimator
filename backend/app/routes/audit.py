from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.schema_models import AuditLog
from ..schemas.api_schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("/", response_model=List[AuditLogResponse])
def get_audit_trail(dataset_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(AuditLog)
    if dataset_id:
        query = query.filter(AuditLog.dataset_id == dataset_id)
    return query.order_by(AuditLog.timestamp.desc()).all()