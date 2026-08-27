from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..config import settings
from ..models.schema_models import Dataset, ReportRecord, AuditLog
from ..services.insight_service import InsightService
from ..services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Automated Reporting"])

class GenerateReportRequest(BaseModel):
    dataset_id: int
    report_type: str = "PDF"  # 'PDF' or 'HTML'
    estimation_data: Optional[Dict[str, Any]] = None

@router.post("/generate")
def generate_report(req: GenerateReportRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    profile = dataset.summary_metrics or {}
    insights = InsightService.generate_rule_based_insights(profile, req.estimation_data)
    
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ext = "pdf" if req.report_type.upper() == "PDF" else "html"
    out_filename = f"report_{dataset.id}_{timestamp_str}.{ext}"
    out_path = settings.REPORTS_DIR / out_filename

    dataset_info = {"id": dataset.id, "filename": dataset.filename}

    if req.report_type.upper() == "PDF":
        ReportService.generate_pdf_report(dataset_info, profile, insights, req.estimation_data, out_path)
    else:
        ReportService.generate_html_report(dataset_info, profile, insights, req.estimation_data, out_path)

    report_rec = ReportRecord(
        dataset_id=dataset.id,
        report_title=f"MoSPI Survey Release - {dataset.filename}",
        report_type=req.report_type.upper(),
        filepath=str(out_path)
    )
    db.add(report_rec)
    
    audit = AuditLog(
        dataset_id=dataset.id,
        action="REPORT_GENERATION",
        module="REPORTING_ENGINE",
        details=f"Generated {req.report_type.upper()} report ({out_filename})."
    )
    db.add(audit)
    db.commit()
    db.refresh(report_rec)

    return {
        "report_id": report_rec.id,
        "filename": out_filename,
        "download_url": f"/api/reports/download/{report_rec.id}"
    }

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
    if not report or not Path(report.filepath).exists():
        raise HTTPException(status_code=404, detail="Report file not found.")

    media_type = "application/pdf" if report.report_type == "PDF" else "text/html"
    return FileResponse(report.filepath, media_type=media_type, filename=Path(report.filepath).name)