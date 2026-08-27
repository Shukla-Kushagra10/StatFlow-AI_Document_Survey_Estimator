from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..models.schema_models import Dataset, AuditLog
from ..services.profile_service import ProfileService
from ..services.clean_service import CleanService
from ..schemas.clean_schema import CleanDatasetRequest, CleanDatasetResponse

router = APIRouter(prefix="/clean", tags=["Data Cleaning"])

@router.post("/execute", response_model=CleanDatasetResponse)
def execute_dataset_cleaning(
    request: CleanDatasetRequest,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset ID {request.dataset_id} not found.")

    raw_path = Path(dataset.filepath)
    if not raw_path.exists():
        raise HTTPException(status_code=404, detail=f"Source dataset file not found at {raw_path}.")

    try:
        df = ProfileService.load_dataset(raw_path)
        original_rows = len(df)
        
        ops_dict = [op.model_dump() for op in request.operations]
        df_cleaned = CleanService.apply_batch_cleaning(df, ops_dict)
        
        # Save processed dataset
        processed_filename = f"cleaned_{dataset.filename}"
        processed_filepath = settings.PROCESSED_DIR / processed_filename
        
        if raw_path.suffix.lower() == ".csv":
            df_cleaned.to_csv(processed_filepath, index=False)
        else:
            df_cleaned.to_excel(processed_filepath, index=False)

        # Update dataset profile & score
        new_profile = ProfileService.generate_full_profile(df_cleaned)
        new_quality = new_profile["quality_score"]["overall_score"]

        dataset.processed_filepath = str(processed_filepath)
        dataset.status = "CLEANED"
        dataset.data_quality_score = new_quality
        dataset.summary_metrics = new_profile
        db.commit()

        # Audit trail logging
        audit_entry = AuditLog(
            dataset_id=dataset.id,
            action="DATA_CLEANING",
            module="CLEANING_ENGINE",
            details=f"Applied {len(request.operations)} cleaning operations. Rows: {original_rows} -> {len(df_cleaned)}. New Quality Score: {new_quality}/100."
        )
        db.add(audit_entry)
        db.commit()

        return CleanDatasetResponse(
            dataset_id=dataset.id,
            original_rows=original_rows,
            cleaned_rows=len(df_cleaned),
            operations_applied=len(request.operations),
            new_quality_score=new_quality,
            output_filename=processed_filename,
            message="Data cleaning completed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleaning operation failed: {str(e)}")