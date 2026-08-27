from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..database import get_db
from ..config import settings
from ..models.schema_models import Dataset, AuditLog
from ..services.profile_service import ProfileService
from ..services.outlier_service import OutlierService

router = APIRouter(prefix="/outliers", tags=["Outlier Detection"])

class OutlierScanRequest(BaseModel):
    dataset_id: int
    method: str = "iqr" # 'iqr', 'zscore'

class OutlierTreatmentRequest(BaseModel):
    dataset_id: int
    treatments: List[Dict[str, Any]]

@router.post("/scan")
def scan_outliers(req: OutlierScanRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    target_path = Path(dataset.processed_filepath if dataset.processed_filepath else dataset.filepath)
    df = ProfileService.load_dataset(target_path)
    anomalies = OutlierService.scan_dataset(df, method=req.method)

    return {
        "dataset_id": dataset.id,
        "method": req.method,
        "total_anomalies": len(anomalies),
        "anomalies": anomalies
    }

@router.post("/treat")
def treat_outliers(req: OutlierTreatmentRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    target_path = Path(dataset.processed_filepath if dataset.processed_filepath else dataset.filepath)
    df = ProfileService.load_dataset(target_path)
    df_treated = OutlierService.apply_treatment(df, req.treatments)

    # Save treated output
    output_filename = f"treated_{dataset.filename}"
    output_path = settings.PROCESSED_DIR / output_filename
    if target_path.suffix.lower() == ".csv":
        df_treated.to_csv(output_path, index=False)
    else:
        df_treated.to_excel(output_path, index=False)

    dataset.processed_filepath = str(output_path)
    new_profile = ProfileService.generate_full_profile(df_treated)
    dataset.data_quality_score = new_profile["quality_score"]["overall_score"]
    dataset.summary_metrics = new_profile
    db.commit()

    # Log audit
    audit = AuditLog(
        dataset_id=dataset.id,
        action="OUTLIER_TREATMENT",
        module="OUTLIER_ENGINE",
        details=f"Applied {len(req.treatments)} outlier treatment rules."
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Outliers treated successfully.",
        "new_quality_score": dataset.data_quality_score
    }