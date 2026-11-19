from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="Compliance Officer")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditSession(Base):
    __tablename__ = "audit_sessions"

    id = Column(String(50), primary_key=True, index=True) # UUID or session_id
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="CREATED") # CREATED, RUNNING, COMPLETED, FAILED
    total_files = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    ambiguous_findings = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0) # 0 to 100
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    files = relationship("ScannedFile", back_populates="session", cascade="all, delete-orphan")
    findings = relationship("PIIFinding", back_populates="session", cascade="all, delete-orphan")
    agent_executions = relationship("AgentExecution", back_populates="session", cascade="all, delete-orphan")
    remediations = relationship("RemediationAction", back_populates="session", cascade="all, delete-orphan")
    compliance_observations = relationship("ComplianceObservation", back_populates="session", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="session", cascade="all, delete-orphan")


class ScannedFile(Base):
    __tablename__ = "scanned_files"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    file_type = Column(String(20), nullable=False) # PDF, DOCX, XLSX, CSV, TXT
    extracted_records_count = Column(Integer, default=0)
    findings_count = Column(Integer, default=0)
    sensitivity_level = Column(String(50), default="LOW") # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="UPLOADED") # UPLOADED, PARSED, ANALYZED, ERROR
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AuditSession", back_populates="files")
    findings = relationship("PIIFinding", back_populates="file", cascade="all, delete-orphan")


class PIIFinding(Base):
    __tablename__ = "pii_findings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("scanned_files.id"), nullable=False)
    
    entity_type = Column(String(100), nullable=False) # PHONE, EMAIL, AADHAAR, PAN, BANK_ACC, PERSON_NAME, etc.
    raw_value = Column(String(500), nullable=False) # Masked in responses, raw in protected processing
    masked_value = Column(String(500), nullable=False)
    
    # Location context
    location = Column(String(255), nullable=True) # e.g., "Page 2" or "Row 15, Col 'Mobile_Number'"
    row_idx = Column(Integer, nullable=True)
    col_name = Column(String(100), nullable=True)
    page_number = Column(Integer, nullable=True)
    
    # Context classification
    classification = Column(String(50), nullable=False) # CONFIRMED_PERSONAL_DATA, LIKELY_PERSONAL_DATA, NON_PERSONAL_IDENTIFIER, AMBIGUOUS
    confidence = Column(Float, nullable=False) # 0.0 to 1.0
    risk_level = Column(String(20), default="LOW") # CRITICAL, HIGH, MEDIUM, LOW
    
    # Explanations and evidence
    explanation = Column(Text, nullable=True)
    detection_method = Column(String(100), default="HYBRID_CONTEXTUAL") # PRESIDIO, DETERMINISTIC, LLM_REASONING, CONTEXT_HEADER
    surrounding_context = Column(Text, nullable=True) # nearby snippet
    
    is_ambiguous = Column(Boolean, default=False)
    verified_by_context = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AuditSession", back_populates="findings")
    file = relationship("ScannedFile", back_populates="findings")
    risk_assessment = relationship("RiskAssessment", uselist=False, back_populates="finding", cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    agent_name = Column(String(100), nullable=False) # Discovery Agent, Context Agent, Risk Agent, Compliance Agent, Remediation Agent
    status = Column(String(50), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    task_description = Column(String(255), nullable=True)
    execution_duration_ms = Column(Integer, default=0)
    findings_count = Column(Integer, default=0)
    logs_json = Column(Text, nullable=True) # Structured JSON array of log events
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    session = relationship("AuditSession", back_populates="agent_executions")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    finding_id = Column(Integer, ForeignKey("pii_findings.id"), nullable=False)
    
    risk_score = Column(Float, nullable=False) # 0 to 100
    risk_category = Column(String(20), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    sensitivity_factor = Column(Float, default=1.0)
    volume_factor = Column(Float, default=1.0)
    exposure_factor = Column(Float, default=1.0)
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    finding = relationship("PIIFinding", back_populates="risk_assessment")


class ComplianceObservation(Base):
    __tablename__ = "compliance_observations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    finding_id = Column(Integer, ForeignKey("pii_findings.id"), nullable=True)
    
    provision_section = Column(String(100), nullable=False) # e.g. "Section 8(5) - Digital Personal Data Protection Act, 2023"
    provision_title = Column(String(255), nullable=False)
    status_in_force = Column(String(50), default="COMMENCED") # COMMENCED, PHASED_COMMENCEMENT, DRAFT_RULES_2025
    observation = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    severity = Column(String(20), default="MEDIUM") # CRITICAL, HIGH, MEDIUM, LOW
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AuditSession", back_populates="compliance_observations")


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("scanned_files.id"), nullable=False)
    finding_id = Column(Integer, ForeignKey("pii_findings.id"), nullable=True)
    
    action_type = Column(String(50), nullable=False) # MASK_DOCUMENT, RESTRICT_ACCESS, RETENTION_REVIEW, PURGE_UNAUTHORIZED
    status = Column(String(50), default="PENDING_APPROVAL") # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED
    original_file_path = Column(String(500), nullable=False)
    redacted_file_path = Column(String(500), nullable=True)
    proposed_details = Column(Text, nullable=False)
    admin_notes = Column(Text, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AuditSession", back_populates="remediations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("audit_sessions.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("AuditSession", back_populates="audit_logs")
