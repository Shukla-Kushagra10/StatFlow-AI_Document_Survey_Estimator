from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema_models import Dataset
from ..services.insight_service import InsightService

router = APIRouter(prefix="/insights", tags=["AI & Analytical Insights"])

@router.get("/{dataset_id}")
def get_insights(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    profile = dataset.summary_metrics or {}
    insights = InsightService.generate_rule_based_insights(profile)
    return {
        "dataset_id": dataset.id,
        "filename": dataset.filename,
        "insights": insights
    }