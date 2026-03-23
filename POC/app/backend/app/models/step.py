"""Step Models - Pydantic models for workflow steps"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class StepStatus(str, Enum):
    """Step execution status"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Step types"""
    INPUT = "input"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    OUTPUT = "output"


class FileInputRequest(BaseModel):
    """File upload request for Step 1"""
    file_name: str
    file_size: int


class DataSummary(BaseModel):
    """Summary of data after processing"""
    row_count: int
    column_count: int
    columns: List[str]
    file_path: str
    first_rows: Optional[List[Dict[str, Any]]] = None


class Step1Response(BaseModel):
    """Response for Step 1 - File Upload"""
    step_id: str = "step_1"
    name: str = "Upload Revenue Files"
    status: StepStatus
    message: str
    data_summary: Optional[DataSummary] = None
    uploaded_files: Optional[List[str]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


class StepDefinition(BaseModel):
    """Definition of a workflow step"""
    id: str
    order: int
    name: str
    description: Optional[str] = None
    type: StepType
    action: str
    params: Dict[str, Any]
    status: StepStatus = StepStatus.IDLE
    error: Optional[str] = None


class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    id: str
    name: str
    description: Optional[str] = None
    steps: List[StepDefinition]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExecutionState(BaseModel):
    """Execution state for a workflow"""
    session_id: str
    workflow_id: str
    current_step_id: str
    step_statuses: Dict[str, StepStatus]
    error: Optional[str] = None
    started_at: datetime
    updated_at: datetime
