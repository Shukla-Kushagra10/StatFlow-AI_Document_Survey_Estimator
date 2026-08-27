import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..models.schema_models import Dataset, AuditLog
from ..services.profile_service import ProfileService
from ..schemas.api_schemas import DatasetResponse

router = APIRouter(prefix="/upload", tags=["Upload & Ingestion"])

@router.post("/", response_model=DatasetResponse)
async def upload_survey_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only CSV (.csv) and Excel (.xlsx, .xls) files are supported."
        )

    dest_path = settings.UPLOAD_DIR / file.filename
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store file on disk: {str(e)}")

    try:
        df = ProfileService.load_dataset(dest_path)
        profile_data = ProfileService.generate_full_profile(df)
    except Exception as e:
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(status_code=422, detail=f"Failed to parse and profile survey file: {str(e)}")

    file_size = dest_path.stat().st_size

    dataset_rec = Dataset(
        filename=file.filename,
        filepath=str(dest_path),
        total_rows=profile_data["total_rows"],
        total_columns=profile_data["total_columns"],
        file_size_bytes=file_size,
        data_quality_score=profile_data["quality_score"]["overall_score"],
        status="RAW",
        summary_metrics=profile_data
    )
    db.add(dataset_rec)
    db.commit()
    db.refresh(dataset_rec)

    audit_entry = AuditLog(
        dataset_id=dataset_rec.id,
        action="DATASET_UPLOAD",
        module="INGESTION",
        details=f"Uploaded '{file.filename}' ({profile_data['total_rows']} rows, {profile_data['total_columns']} cols)."
    )
    db.add(audit_entry)
    db.commit()

    return dataset_rec