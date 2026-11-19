"""
FastAPI Application for PRIVESCAN AI.
Exposes REST endpoints for the multi-agent privacy auditing system.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from backend.app.config import settings, UPLOADS_DIR, REMEDIATED_DIR, REPORTS_DIR
from backend.app.database import get_db, Base, engine
from backend.app.models import (
    AuditSession, ScannedFile, PIIFinding, AgentExecution,
    ComplianceObservation, RemediationAction, AuditLog
)
from backend.app.schemas import (
    AuditSessionCreate, AuditSessionResponse, ScannedFileResponse,
    PIIFindingResponse, AgentExecutionResponse, ComplianceObservationResponse,
    RemediationActionResponse, RemediationApprovalRequest, AuditLogResponse,
    DashboardStatsResponse, ContextClassificationRequest, ContextClassificationResponse
)
from backend.app.services.audit_service import AuditService
from backend.app.engine.context_classifier import context_engine

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic AI-Powered Data Privacy Discovery & DPDP Compliance Auditor"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OPERATIONAL",
        "llm_provider": settings.LLM_PROVIDER,
        "model": settings.GEMINI_MODEL,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }

# ----------------- AUDIT SESSIONS & WORKFLOW -----------------

@app.post("/api/audit/session", response_model=AuditSessionResponse)
def create_session(data: AuditSessionCreate, db: Session = Depends(get_db)):
    session = AuditService.create_session(db, title=data.title)
    return session

@app.get("/api/audit/sessions", response_model=List[AuditSessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(AuditSession).order_by(AuditSession.created_at.desc()).all()

@app.get("/api/audit/session/{session_id}", response_model=AuditSessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(AuditSession).filter(AuditSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Audit session not found")
    return session

@app.post("/api/audit/upload", response_model=List[ScannedFileResponse])
async def upload_files(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(AuditSession).filter(AuditSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Audit session not found")

    saved_files = []
    for f in files:
        # Sanitize filename
        safe_name = Path(f.filename).name.replace(" ", "_")
        dest_path = UPLOADS_DIR / f"{session_id}_{safe_name}"
        
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
            
        file_size = dest_path.stat().st_size
        ext = dest_path.suffix.upper().replace(".", "")
        
        scanned_file = AuditService.register_scanned_file(
            db=db,
            session_id=session_id,
            filename=safe_name,
            file_path=str(dest_path),
            file_size=file_size,
            file_type=ext
        )
        saved_files.append(scanned_file)
        
    return saved_files

@app.post("/api/audit/execute/{session_id}", response_model=AuditSessionResponse)
def execute_audit(session_id: str, db: Session = Depends(get_db)):
    try:
        session = AuditService.execute_audit_session(db, session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audit/demo", response_model=AuditSessionResponse)
def trigger_demo_audit(db: Session = Depends(get_db)):
    """One-click trigger: Loads the 3 synthetic demonstration benchmark files and executes the audit."""
    session = AuditService.load_demo_session(db)
    return session

# ----------------- DASHBOARD ANALYTICS -----------------

@app.get("/api/audit/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    stats = AuditService.get_dashboard_stats(db, session_id)
    return stats

# ----------------- FINDINGS EXPLORER -----------------

@app.get("/api/findings", response_model=List[PIIFindingResponse])
def get_findings(
    session_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    entity_type: Optional[str] = None,
    classification: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PIIFinding)
    if session_id:
        query = query.filter(PIIFinding.session_id == session_id)
    if risk_level and risk_level.upper() != "ALL":
        query = query.filter(PIIFinding.risk_level == risk_level.upper())
    if entity_type and entity_type.upper() != "ALL":
        query = query.filter(PIIFinding.entity_type == entity_type.upper())
    if classification and classification.upper() != "ALL":
        query = query.filter(PIIFinding.classification == classification.upper())
    if search:
        s = f"%{search}%"
        query = query.filter(
            (PIIFinding.entity_type.ilike(s)) |
            (PIIFinding.col_name.ilike(s)) |
            (PIIFinding.explanation.ilike(s)) |
            (PIIFinding.location.ilike(s))
        )
    
    findings = query.order_by(PIIFinding.id.desc()).all()
    
    # Attach file_name
    res = []
    for f in findings:
        resp = PIIFindingResponse.from_orm(f)
        resp.file_name = f.file.filename if f.file else "Document"
        res.append(resp)
    return res

@app.get("/api/findings/{finding_id}")
def get_finding_detail(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(PIIFinding).filter(PIIFinding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    risk = f.risk_assessment
    comp_obs = db.query(ComplianceObservation).filter(ComplianceObservation.session_id == f.session_id).all()
    
    return {
        "finding": PIIFindingResponse.from_orm(f),
        "file_name": f.file.filename if f.file else "Document",
        "risk_assessment": {
            "score": risk.risk_score if risk else f.risk_score,
            "category": risk.risk_category if risk else f.risk_level,
            "rationale": risk.rationale if risk else f.explanation
        } if risk else None,
        "related_dpdp_observations": [
            {
                "section": obs.provision_section,
                "title": obs.provision_title,
                "observation": obs.observation,
                "recommendation": obs.recommendation,
                "severity": obs.severity
            }
            for obs in comp_obs
        ]
    }

# ----------------- DPDP COMPLIANCE CENTER -----------------

@app.get("/api/compliance", response_model=List[ComplianceObservationResponse])
def get_compliance_observations(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ComplianceObservation)
    if session_id:
        query = query.filter(ComplianceObservation.session_id == session_id)
    return query.order_by(ComplianceObservation.id.desc()).all()

# ----------------- REMEDIATION CENTER -----------------

@app.get("/api/remediation", response_model=List[RemediationActionResponse])
def get_remediation_actions(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RemediationAction)
    if session_id:
        query = query.filter(RemediationAction.session_id == session_id)
    actions = query.order_by(RemediationAction.id.desc()).all()
    
    res = []
    for a in actions:
        resp = RemediationActionResponse.from_orm(a)
        resp.file_name = a.session.files[0].filename if a.session and a.session.files else "File"
        resp.has_redacted_copy = bool(a.redacted_file_path and Path(a.redacted_file_path).exists())
        res.append(resp)
    return res

@app.post("/api/remediation/approve", response_model=RemediationActionResponse)
def approve_remediation_action(req: RemediationApprovalRequest, db: Session = Depends(get_db)):
    action = AuditService.approve_remediation(
        db=db,
        action_id=req.action_id,
        approve=req.approve,
        admin_notes=req.admin_notes
    )
    resp = RemediationActionResponse.from_orm(action)
    resp.has_redacted_copy = bool(action.redacted_file_path and Path(action.redacted_file_path).exists())
    return resp

@app.get("/api/remediation/download/{action_id}")
def download_redacted_document(action_id: int, db: Session = Depends(get_db)):
    action = db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
    if not action or not action.redacted_file_path:
        raise HTTPException(status_code=404, detail="Redacted file not found")
        
    path = Path(action.redacted_file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical redacted file does not exist")
        
    return FileResponse(
        str(path),
        filename=path.name,
        media_type="application/octet-stream"
    )

# ----------------- AGENT ACTIVITY CENTER -----------------

@app.get("/api/agents/status", response_model=List[AgentExecutionResponse])
def get_agents_status(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AgentExecution)
    if session_id:
        query = query.filter(AgentExecution.session_id == session_id)
    return query.order_by(AgentExecution.id.desc()).all()

# ----------------- REPORT GENERATOR -----------------

@app.get("/api/inventory")
def get_data_inventory_report(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    DATA INVENTORY REPORT: Showing which personal data is held where.
    Outputs structured mapping of files -> extractors -> sensitivity -> locations -> personal data categories.
    """
    query = db.query(ScannedFile)
    if session_id:
        query = query.filter(ScannedFile.session_id == session_id)
    files = query.all()
    
    inventory = []
    for f in files:
        file_findings = [
            find for find in f.findings 
            if find.classification in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"]
        ]
        cat_counts = {}
        locations = []
        for find in file_findings:
            cat_counts[find.entity_type] = cat_counts.get(find.entity_type, 0) + 1
            if len(locations) < 15:
                locations.append({
                    "entity_type": find.entity_type,
                    "masked_value": find.masked_value,
                    "location": find.location or f"Row {find.row_idx or 1}",
                    "col_name": find.col_name or "",
                    "risk_level": find.risk_level
                })
                
        ext_upper = (f.file_type or "").upper()
        extractor_name = "PyMuPDF (PDF Parser)" if "PDF" in ext_upper else (
            "Pandas & Openpyxl (Spreadsheet Parser)" if any(x in ext_upper for x in ["XLS", "CSV"]) else (
                "Multimodal AI OCR Extractor" if any(x in ext_upper for x in ["PNG", "JPG", "JPEG", "TIFF"]) else "Structured Text Parser"
            )
        )
        
        inventory.append({
            "file_id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "extractor_used": extractor_name,
            "file_size_bytes": f.file_size_bytes,
            "sensitivity_level": getattr(f, "sensitivity_level", "LOW") or "LOW",
            "total_personal_records": len(file_findings),
            "categories_held": cat_counts,
            "sample_locations": locations,
            "status": f.status
        })
        
    return {
        "total_files": len(files),
        "inventory": inventory
    }

@app.get("/api/reports/download/{session_id}")
def download_session_report(session_id: str, db: Session = Depends(get_db)):
    try:
        report_pdf_path = AuditService.generate_session_report_pdf(db, session_id)
        path = Path(report_pdf_path)
        if not path.exists():
            raise HTTPException(status_code=500, detail="Report generation failed")
            
        return FileResponse(
            str(path),
            filename=path.name,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- CONTEXT CLASSIFICATION TESTING -----------------

@app.post("/api/context/test", response_model=ContextClassificationResponse)
def test_context_engine(req: ContextClassificationRequest):
    """
    Direct endpoint demonstrating the context differentiator:
    Order ID: 9876543210 -> NON_PERSONAL_IDENTIFIER
    Mobile_Number: 9876543210 -> CONFIRMED_PERSONAL_DATA
    """
    result = context_engine.classify_candidate(
        value=req.value,
        column_name=req.column_name,
        document_type=req.document_type,
        surrounding_text=req.surrounding_text
    )
    return ContextClassificationResponse(**result)
