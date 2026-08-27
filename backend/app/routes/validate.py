from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..database import get_db
from ..models.schema_models import Dataset, AuditLog
from ..services.profile_service import ProfileService
from ..services.validate_service import ValidateService

router = APIRouter(prefix="/validate", tags=["Validation Engine"])

class ValidationRunRequest(BaseModel):
    dataset_id: int
    custom_rules: Optional[List[Dict[str, Any]]] = None

@router.post("/run")
def run_validation(req: ValidationRunRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    target_path = Path(dataset.processed_filepath if dataset.processed_filepath else dataset.filepath)
    df = ProfileService.load_dataset(target_path)

    rules = req.custom_rules if req.custom_rules else ValidateService.get_standard_mospi_rules()
    violations = ValidateService.evaluate_rules(df, rules)

    # Log audit
    audit = AuditLog(
        dataset_id=dataset.id,
        action="DATA_VALIDATION",
        module="VALIDATION_ENGINE",
        details=f"Ran {len(rules)} validation rules. Found {len(violations)} violations."
    )
    db.add(audit)
    db.commit()

    return {
        "dataset_id": dataset.id,
        "rules_evaluated": len(rules),
        "total_violations": len(violations),
        "violations": violations
    }