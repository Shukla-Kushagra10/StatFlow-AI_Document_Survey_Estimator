from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models.schema_models import Dataset, AuditLog
from ..services.profile_service import ProfileService
from ..services.estimation_service import EstimationService

router = APIRouter(prefix="/estimation", tags=["Statistical Estimation"])

class EstimateRequest(BaseModel):
    dataset_id: int
    target_column: str
    weight_column: Optional[str] = "survey_weight"
    confidence_level: Optional[float] = 0.95

@router.post("/compute")
def compute_survey_estimates(req: EstimateRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    target_path = Path(dataset.processed_filepath if dataset.processed_filepath else dataset.filepath)
    df = ProfileService.load_dataset(target_path)

    try:
        estimation_result = EstimationService.estimate_parameter(
            df=df,
            target_col=req.target_column,
            weight_col=req.weight_column,
            confidence_level=req.confidence_level
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Audit entry
    audit = AuditLog(
        dataset_id=dataset.id,
        action="STATISTICAL_ESTIMATION",
        module="ESTIMATION_ENGINE",
        details=f"Computed weighted & unweighted estimates for '{req.target_column}' at {int(req.confidence_level * 100)}% CI."
    )
    db.add(audit)
    db.commit()

    return estimation_result