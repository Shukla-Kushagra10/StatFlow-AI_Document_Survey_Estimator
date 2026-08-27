from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from datetime import datetime
from app.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    processed_filepath = Column(String(512), nullable=True)
    total_rows = Column(Integer, default=0)
    total_columns = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    data_quality_score = Column(Float, default=0.0)
    status = Column(String(50), default="RAW") # RAW, CLEANED, WEIGHTED, ESTIMATED
    created_at = Column(DateTime, default=datetime.utcnow)
    summary_metrics = Column(JSON, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, index=True, nullable=True)
    action = Column(String(100), nullable=False)
    module = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, index=True)
    rule_name = Column(String(100), nullable=False)
    column_name = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False) # e.g., 'gte', 'lte', 'between', 'in', 'custom'
    parameters = Column(JSON, nullable=True)
    severity = Column(String(20), default="ERROR") # ERROR, WARNING

class ReportRecord(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, index=True)
    report_title = Column(String(255), nullable=False)
    report_type = Column(String(10), nullable=False) # PDF, HTML
    filepath = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)