from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional

from ..database import get_db
from ..config import settings
from ..models.schema_models import Dataset, AuditLog
from ..services.profile_service import ProfileService
from ..services.weighting_service import WeightingService

router = APIRouter(prefix="/weighting", tags=["Survey Weighting Engine"])

class PostStratifyRequest(BaseModel):
    dataset_id: int
    strata_col: str
    population_distribution: Dict[str, float]
    base_weight_col: Optional[str] = None
    output_weight_col: str = "adjusted_weight"

class RakingRequest(BaseModel):
    dataset_id: int
    margins: Dict[str, Dict[str, float]]
    base_weight_col: Optional[str] = None
    output_weight_col: str = "raked_weight"

@router.post("/post-stratify")
def run_post_stratification(req: PostStratifyRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    target_path = Path(dataset.processed_filepath if dataset.processed_filepath else dataset.filepath)
    df = ProfileService.load_dataset(target_path)

    new_weights = WeightingService.post_stratify(
        df,
        strata_col=req.strata_col,
        pop_distribution=req.population_distribution,
        base_weight_col=req.base_weight_col
    )
    df[req.output_weight_col] = new_weights
    diagnostics = WeightingService.calculate_weight_diagnostics(new_weights)

    # Save modified data
    output_filename = f"weighted_{dataset.filename}"
    output_path = settings.PROCESSED_DIR / output_filename
    if target_path.suffix.lower() == ".csv":
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)

    dataset.processed_filepath = str(output_path)
    dataset.status = "WEIGHTED"
    dataset.summary_metrics = ProfileService.generate_full_profile(df)
    db.commit()

    # Log audit
    audit = AuditLog(
        dataset_id=dataset.id,
        action="SURVEY_WEIGHTING",
        module="POST_STRATIFICATION",
        details=f"Post-stratified on '{req.strata_col}'. Eff Sample Size: {diagnostics['effective_sample_size']}."
    )
    db.add(audit)
    db.commit()

    return {
        "dataset_id": dataset.id,
        "method": "Post-Stratification",
        "output_weight_column": req.output_weight_col,
        "diagnostics": diagnostics
    }

@router.post("/raking")
def run_raking(req: RakingRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    target_path = Path(dataset.processed_filepath if dataset.processed_filepath else dataset.filepath)
    df = ProfileService.load_dataset(target_path)

    new_weights = WeightingService.rake(
        df,
        margins=req.margins,
        base_weight_col=req.base_weight_col
    )
    df[req.output_weight_col] = new_weights
    diagnostics = WeightingService.calculate_weight_diagnostics(new_weights)

    # Save output
    output_filename = f"raked_{dataset.filename}"
    output_path = settings.PROCESSED_DIR / output_filename
    if target_path.suffix.lower() == ".csv":
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)

    dataset.processed_filepath = str(output_path)
    dataset.status = "WEIGHTED"
    dataset.summary_metrics = ProfileService.generate_full_profile(df)
    db.commit()

    # Log audit
    audit = AuditLog(
        dataset_id=dataset.id,
        action="SURVEY_WEIGHTING",
        module="RAKING_CALIBRATION",
        details=f"Applied raking across {list(req.margins.keys())}. Eff Sample Size: {diagnostics['effective_sample_size']}."
    )
    db.add(audit)
    db.commit()

    return {
        "dataset_id": dataset.id,
        "method": "Raking / Calibration",
        "output_weight_column": req.output_weight_col,
        "diagnostics": diagnostics
    }