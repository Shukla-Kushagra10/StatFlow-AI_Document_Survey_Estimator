from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema_models import Dataset

router = APIRouter(prefix="/profile", tags=["Data Profiling"])

@router.get("/{dataset_id}")
def get_dataset_profile(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset_id} not found.")

    return {
        "dataset_id": dataset.id,
        "filename": dataset.filename,
        "status": dataset.status,
        "created_at": dataset.created_at,
        "profile": dataset.summary_metrics
    }