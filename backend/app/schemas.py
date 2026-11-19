from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# PII Finding Schemas
class PIIFindingBase(BaseModel):
    entity_type: str
    masked_value: str
    location: Optional[str] = None
    row_idx: Optional[int] = None
    col_name: Optional[str] = None
    page_number: Optional[int] = None
    classification: str
    confidence: float
    risk_level: str
    explanation: Optional[str] = None
    detection_method: str = "HYBRID_CONTEXTUAL"
    surrounding_context: Optional[str] = None
    is_ambiguous: bool = False
    verified_by_context: bool = True

class PIIFindingResponse(PIIFindingBase):
    id: int
    session_id: str
    file_id: int
    file_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Scanned File Schemas
class ScannedFileResponse(BaseModel):
    id: int
    session_id: str
    filename: str
    file_size_bytes: int
    file_type: str
    extracted_records_count: int
    findings_count: int
    sensitivity_level: Optional[str] = "LOW"
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Agent Execution Schemas
class AgentExecutionResponse(BaseModel):
    id: int
    session_id: str
    agent_name: str
    status: str
    task_description: Optional[str] = None
    execution_duration_ms: int
    findings_count: int
    logs_json: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Risk Assessment Schemas
class RiskAssessmentResponse(BaseModel):
    id: int
    session_id: str
    finding_id: int
    risk_score: float
    risk_category: str
    sensitivity_factor: float
    volume_factor: float
    exposure_factor: float
    rationale: str
    created_at: datetime

    class Config:
        from_attributes = True

# Compliance Observation Schemas
class ComplianceObservationResponse(BaseModel):
    id: int
    session_id: str
    finding_id: Optional[int] = None
    provision_section: str
    provision_title: str
    status_in_force: str
    observation: str
    evidence: str
    recommendation: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True

# Remediation Action Schemas
class RemediationActionResponse(BaseModel):
    id: int
    session_id: str
    file_id: int
    file_name: Optional[str] = None
    finding_id: Optional[int] = None
    action_type: str
    status: str
    original_file_path: str
    redacted_file_path: Optional[str] = None
    has_redacted_copy: bool = False
    proposed_details: str
    admin_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RemediationApprovalRequest(BaseModel):
    action_id: int
    approve: bool
    admin_notes: Optional[str] = None

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    session_id: str
    agent_name: str
    action: str
    details: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Audit Session Schemas
class AuditSessionCreate(BaseModel):
    title: Optional[str] = "Organization Privacy & DPDP Compliance Audit"

class AuditSessionResponse(BaseModel):
    id: str
    title: str
    status: str
    total_files: int
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    ambiguous_findings: int
    risk_score: float
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Dashboard Stats Schema
class DashboardStatsResponse(BaseModel):
    total_files_scanned: int
    total_findings: int
    high_risk_findings: int
    ambiguous_detections: int
    files_requiring_remediation: int
    audit_completion_percentage: float
    overall_risk_score: float
    pii_categories_distribution: Dict[str, int]
    risk_severity_distribution: Dict[str, int]
    files_by_type: Dict[str, int]
    findings_by_file_type: Dict[str, int]
    recent_activity: List[AuditLogResponse]
    agent_statuses: List[AgentExecutionResponse]

# Context Classification Test Request / Response
class ContextClassificationRequest(BaseModel):
    column_name: str
    value: str
    document_type: str
    surrounding_text: Optional[str] = ""

class ContextClassificationResponse(BaseModel):
    classification: str
    confidence: float
    reason: str
    entity_type: str
    is_personal_data: bool
