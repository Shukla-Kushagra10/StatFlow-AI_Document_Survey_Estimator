from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CleaningOperation(BaseModel):
    type: str # 'impute', 'deduplicate', 'strip_whitespace'
    column: Optional[str] = None
    method: Optional[str] = None # 'mean', 'median', 'mode', 'knn', 'regression', 'drop', 'constant'
    fill_value: Optional[Any] = None
    n_neighbors: Optional[int] = 5

class CleanDatasetRequest(BaseModel):
    dataset_id: int
    operations: List[CleaningOperation]

class CleanDatasetResponse(BaseModel):
    dataset_id: int
    original_rows: int
    cleaned_rows: int
    operations_applied: int
    new_quality_score: float
    output_filename: str
    message: str