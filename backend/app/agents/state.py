"""
Shared State Schema for the PRIVESCAN AI Multi-Agent LangGraph Workflow.
"""

from typing import List, Dict, Any, Optional, Annotated
import operator
from pydantic import BaseModel, Field

class AgentFinding(BaseModel):
    file_id: int
    file_name: str
    entity_type: str
    raw_value: str
    masked_value: str
    location: str
    row_idx: Optional[int] = None
    col_name: Optional[str] = None
    page_number: Optional[int] = None
    classification: str # CONFIRMED_PERSONAL_DATA, LIKELY_PERSONAL_DATA, NON_PERSONAL_IDENTIFIER, AMBIGUOUS
    confidence: float
    risk_level: str = "LOW"
    risk_score: float = 0.0
    explanation: str
    detection_method: str = "HYBRID_CONTEXTUAL"
    surrounding_context: Optional[str] = None
    is_ambiguous: bool = False
    verified_by_context: bool = True

class AgentState(BaseModel):
    session_id: str
    file_paths: List[str] = Field(default_factory=list)
    file_ids: List[int] = Field(default_factory=list)
    
    # Workflow control
    current_phase: str = "PLANNING"
    task_plan: List[str] = Field(default_factory=list)
    
    # Discovered records from Discovery Agent
    discovered_records: List[Dict[str, Any]] = Field(default_factory=list)
    file_inventory: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Processed findings from Context Agent
    findings: List[AgentFinding] = Field(default_factory=list)
    ambiguous_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    needs_extra_verification: bool = False
    
    # Risk Assessment
    overall_risk_score: float = 0.0
    risk_distribution: Dict[str, int] = Field(default_factory=lambda: {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0})
    risk_assessments: List[Dict[str, Any]] = Field(default_factory=list)
    file_sensitivity: Dict[str, str] = Field(default_factory=dict)
    
    # DPDP Compliance
    compliance_observations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Remediation
    remediation_actions: List[Dict[str, Any]] = Field(default_factory=list)
    redacted_files: List[str] = Field(default_factory=list)
    
    # Audit trail & Logs
    audit_logs: List[Dict[str, Any]] = Field(default_factory=list)
    agent_executions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Error handling
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
