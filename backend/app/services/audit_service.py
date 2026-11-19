"""
Audit Service.
Coordinates database persistence, multi-agent workflow invocation,
remediation approvals, and dashboard metrics computation.
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.config import settings, UPLOADS_DIR, SAMPLE_DATA_DIR
from backend.app.database import engine, Base
from backend.app.models import (
    AuditSession, ScannedFile, PIIFinding, AgentExecution,
    RiskAssessment, ComplianceObservation, RemediationAction, AuditLog
)
from backend.app.agents.state import AgentState
from backend.app.agents.orchestrator import orchestrator_app
from backend.app.services.report_service import ReportService

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

class AuditService:
    @staticmethod
    def create_session(db: Session, title: str = "Privacy & DPDP Compliance Audit") -> AuditSession:
        session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
        session = AuditSession(
            id=session_id,
            title=title,
            status="CREATED",
            created_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def register_scanned_file(
        db: Session,
        session_id: str,
        filename: str,
        file_path: str,
        file_size: int,
        file_type: str
    ) -> ScannedFile:
        scanned_file = ScannedFile(
            session_id=session_id,
            filename=filename,
            original_path=file_path,
            file_size_bytes=file_size,
            file_type=file_type.upper(),
            status="UPLOADED"
        )
        db.add(scanned_file)
        db.commit()
        db.refresh(scanned_file)
        return scanned_file

    @staticmethod
    def execute_audit_session(db: Session, session_id: str) -> AuditSession:
        """Runs the complete multi-agent LangGraph pipeline on all files in the session."""
        session = db.query(AuditSession).filter(AuditSession.id == session_id).first()
        if not session:
            raise ValueError(f"Audit session {session_id} not found.")

        session.status = "RUNNING"
        db.commit()

        # Query files for this session
        files = db.query(ScannedFile).filter(ScannedFile.session_id == session_id).all()
        if not files:
            session.status = "FAILED"
            db.commit()
            return session

        file_paths = [f.original_path for f in files]
        file_ids = [f.id for f in files]

        # Construct Initial LangGraph State
        initial_state = AgentState(
            session_id=session_id,
            file_paths=file_paths,
            file_ids=file_ids,
            current_phase="PLANNING"
        )

        # Execute LangGraph Workflow
        final_state_dict = orchestrator_app.invoke(initial_state)

        # Convert state dictionary to AgentState if needed
        state = AgentState(**final_state_dict) if isinstance(final_state_dict, dict) else final_state_dict

        # Persist File Inventory Updates
        file_lookup = {f.id: f for f in files}
        file_id_by_name = {f.filename: f.id for f in files}

        for inv in state.file_inventory:
            f_id = inv.get("file_id")
            if f_id in file_lookup:
                file_lookup[f_id].extracted_records_count = inv.get("records_count", 0)
                file_lookup[f_id].status = inv.get("status", "PARSED")

        # Persist Agent Executions & Logs
        for ag_name, ag_data in state.agent_executions.items():
            exec_record = AgentExecution(
                session_id=session_id,
                agent_name=ag_name,
                status=ag_data.get("status", "COMPLETED"),
                task_description=ag_data.get("task_description", ""),
                execution_duration_ms=ag_data.get("execution_duration_ms", 0),
                findings_count=ag_data.get("findings_count", 0),
                logs_json=json.dumps(ag_data.get("logs", [])),
                completed_at=datetime.utcnow()
            )
            db.add(exec_record)

        # Persist Audit Logs
        for log_entry in state.audit_logs:
            audit_log = AuditLog(
                session_id=session_id,
                agent_name=log_entry.get("agent_name", "Orchestrator"),
                action=log_entry.get("action", "INFO"),
                details=log_entry.get("details", ""),
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)

        # Persist Findings and Risk Assessments
        crit_count = 0
        high_count = 0
        med_count = 0
        low_count = 0
        amb_count = 0

        for f in state.findings:
            target_f_id = f.file_id
            if target_f_id not in file_lookup:
                target_f_id = file_id_by_name.get(f.file_name, files[0].id)

            finding_model = PIIFinding(
                session_id=session_id,
                file_id=target_f_id,
                entity_type=f.entity_type,
                raw_value=f.raw_value,
                masked_value=f.masked_value,
                location=f.location,
                row_idx=f.row_idx,
                col_name=f.col_name,
                page_number=f.page_number,
                classification=f.classification,
                confidence=f.confidence,
                risk_level=f.risk_level,
                explanation=f.explanation,
                detection_method=f.detection_method,
                surrounding_context=f.surrounding_context,
                is_ambiguous=f.is_ambiguous,
                verified_by_context=f.verified_by_context,
                created_at=datetime.utcnow()
            )
            db.add(finding_model)
            db.flush() # Populate finding_model.id

            # Create Risk Assessment record
            risk_rec = RiskAssessment(
                session_id=session_id,
                finding_id=finding_model.id,
                risk_score=f.risk_score,
                risk_category=f.risk_level,
                sensitivity_factor=1.0,
                volume_factor=1.0,
                exposure_factor=1.0,
                rationale=f.explanation,
                created_at=datetime.utcnow()
            )
            db.add(risk_rec)

            # Update count aggregates
            if f.risk_level == "CRITICAL":
                crit_count += 1
            elif f.risk_level == "HIGH":
                high_count += 1
            elif f.risk_level == "MEDIUM":
                med_count += 1
            else:
                low_count += 1

            if f.is_ambiguous:
                amb_count += 1

        # Persist Compliance Observations
        for obs in state.compliance_observations:
            comp_rec = ComplianceObservation(
                session_id=session_id,
                finding_id=None,
                provision_section=obs.get("provision_section", "DPDP Act, 2023"),
                provision_title=obs.get("provision_title", "General Obligation"),
                status_in_force=obs.get("status_in_force", "COMMENCED"),
                observation=obs.get("observation", ""),
                evidence=obs.get("evidence", ""),
                recommendation=obs.get("recommendation", ""),
                severity=obs.get("severity", "MEDIUM"),
                created_at=datetime.utcnow()
            )
            db.add(comp_rec)

        # Persist Remediation Actions
        for rem in state.remediation_actions:
            rem_f_id = rem.get("file_id")
            if rem_f_id not in file_lookup:
                rem_f_id = file_id_by_name.get(rem.get("file_name"), files[0].id)

            rem_rec = RemediationAction(
                session_id=session_id,
                file_id=rem_f_id,
                finding_id=None,
                action_type=rem.get("action_type", "MASK_DOCUMENT"),
                status=rem.get("status", "PENDING_APPROVAL"),
                original_file_path=rem.get("original_file_path", ""),
                redacted_file_path=rem.get("redacted_file_path"),
                proposed_details=rem.get("proposed_details", ""),
                admin_notes=rem.get("admin_notes"),
                created_at=datetime.utcnow()
            )
            db.add(rem_rec)

        # Update Session Summary
        # Update individual file sensitivity levels
        for f in files:
            sens = state.file_sensitivity.get(f.filename, "LOW")
            f.sensitivity_level = sens
            f.status = "ANALYZED"

        session.status = "COMPLETED"
        session.total_files = len(files)
        session.total_findings = len(state.findings)
        session.critical_findings = crit_count
        session.high_findings = high_count
        session.medium_findings = med_count
        session.low_findings = low_count
        session.ambiguous_findings = amb_count
        session.risk_score = state.overall_risk_score
        session.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def load_demo_session(db: Session) -> AuditSession:
        """Loads the 3 synthetic demonstration files and immediately executes an end-to-end audit."""
        title = "Enterprise Demonstration Audit - DPDP Compliance"
        session = AuditService.create_session(db, title=title)

        sample_files = [
            ("customer_database.xlsx", "XLSX"),
            ("employee_records.pdf", "PDF"),
            ("old_customer_export.csv", "CSV"),
            ("scanned_kyc_application.png", "PNG")
        ]

        for fname, ftype in sample_files:
            sample_path = SAMPLE_DATA_DIR / fname
            if not sample_path.exists():
                from backend.sample_data.generate_samples import (
                    generate_customer_database_excel,
                    generate_old_customer_export_csv,
                    generate_employee_records_pdf,
                    generate_scanned_image_sample
                )
                generate_customer_database_excel()
                generate_old_customer_export_csv()
                generate_employee_records_pdf()
                generate_scanned_image_sample()

            stat = sample_path.stat()
            AuditService.register_scanned_file(
                db=db,
                session_id=session.id,
                filename=fname,
                file_path=str(sample_path),
                file_size=stat.st_size,
                file_type=ftype
            )

        # Execute Audit
        AuditService.execute_audit_session(db, session.id)
        return session

    @staticmethod
    def approve_remediation(db: Session, action_id: int, approve: bool, admin_notes: Optional[str] = None) -> RemediationAction:
        action = db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        if not action:
            raise ValueError(f"Remediation action {action_id} not found.")

        action.status = "APPROVED" if approve else "REJECTED"
        action.admin_notes = admin_notes or ("Approved by Compliance Officer" if approve else "Rejected during review")
        action.approved_at = datetime.utcnow()

        # Add Audit Log
        log_entry = AuditLog(
            session_id=action.session_id,
            agent_name="Compliance Administrator (Human-in-the-Loop)",
            action=f"REMEDIATION_{action.status}",
            details=f"Remediation action '{action.action_type}' for {action.original_file_path} was {action.status.lower()} with notes: {action.admin_notes}",
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def get_dashboard_stats(db: Session, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates dynamic real statistics for the active session (or global if not specified)."""
        files_q = db.query(ScannedFile)
        findings_q = db.query(PIIFinding)
        rem_q = db.query(RemediationAction)
        logs_q = db.query(AuditLog)
        agents_q = db.query(AgentExecution)

        if session_id:
            files_q = files_q.filter(ScannedFile.session_id == session_id)
            findings_q = findings_q.filter(PIIFinding.session_id == session_id)
            rem_q = rem_q.filter(RemediationAction.session_id == session_id)
            logs_q = logs_q.filter(AuditLog.session_id == session_id)
            agents_q = agents_q.filter(AgentExecution.session_id == session_id)

        total_files = files_q.count()
        total_findings = findings_q.count()
        high_risk_findings = findings_q.filter(PIIFinding.risk_level.in_(["CRITICAL", "HIGH"])).count()
        ambiguous_detections = findings_q.filter(PIIFinding.is_ambiguous == True).count()
        files_remediation = rem_q.filter(RemediationAction.status == "PENDING_APPROVAL").count()

        # PII Categories Distribution
        cat_counts = (
            findings_q.with_entities(PIIFinding.entity_type, func.count(PIIFinding.id))
            .group_by(PIIFinding.entity_type)
            .all()
        )
        pii_dist = {cat: count for cat, count in cat_counts}

        # Risk Severity Distribution
        risk_counts = (
            findings_q.with_entities(PIIFinding.risk_level, func.count(PIIFinding.id))
            .group_by(PIIFinding.risk_level)
            .all()
        )
        risk_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for r_level, count in risk_counts:
            if r_level in risk_dist:
                risk_dist[r_level] = count

        # Files by Type
        file_types = (
            files_q.with_entities(ScannedFile.file_type, func.count(ScannedFile.id))
            .group_by(ScannedFile.file_type)
            .all()
        )
        files_by_type = {ft: count for ft, count in file_types}

        # Findings by File Type
        findings_by_file_type = {}
        for f in findings_q.all():
            f_type = f.file.file_type if f.file else "OTHER"
            findings_by_file_type[f_type] = findings_by_file_type.get(f_type, 0) + 1

        # Recent Activity
        recent_logs = (
            logs_q
            .order_by(AuditLog.timestamp.desc())
            .limit(10)
            .all()
        )

        # Agent Executions
        agent_execs = (
            agents_q
            .order_by(AgentExecution.id.desc())
            .limit(10)
            .all()
        )

        # Overall average or session-specific risk score
        if session_id:
            sess = db.query(AuditSession).filter(AuditSession.id == session_id).first()
            avg_score = sess.risk_score if sess else 0.0
        else:
            avg_score = db.query(func.avg(AuditSession.risk_score)).scalar() or 0.0

        return {
            "total_files_scanned": total_files,
            "total_findings": total_findings,
            "high_risk_findings": high_risk_findings,
            "ambiguous_detections": ambiguous_detections,
            "files_requiring_remediation": files_remediation,
            "audit_completion_percentage": 100.0 if total_files > 0 else 0.0,
            "overall_risk_score": round(float(avg_score), 1),
            "pii_categories_distribution": pii_dist,
            "risk_severity_distribution": risk_dist,
            "files_by_type": files_by_type,
            "findings_by_file_type": findings_by_file_type,
            "recent_activity": recent_logs,
            "agent_statuses": agent_execs
        }

    @staticmethod
    def generate_session_report_pdf(db: Session, session_id: str) -> str:
        session = db.query(AuditSession).filter(AuditSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        findings_objs = db.query(PIIFinding).filter(PIIFinding.session_id == session_id).all()
        findings_dicts = [
            {
                "file_name": f.file.filename if f.file else "File",
                "masked_value": f.masked_value,
                "entity_type": f.entity_type,
                "classification": f.classification,
                "risk_level": f.risk_level,
                "confidence": f.confidence
            }
            for f in findings_objs
        ]

        obs_objs = db.query(ComplianceObservation).filter(ComplianceObservation.session_id == session_id).all()
        obs_dicts = [
            {
                "provision_section": o.provision_section,
                "provision_title": o.provision_title,
                "status_in_force": o.status_in_force,
                "observation": o.observation,
                "evidence": o.evidence,
                "recommendation": o.recommendation,
                "severity": o.severity
            }
            for o in obs_objs
        ]

        rem_objs = db.query(RemediationAction).filter(RemediationAction.session_id == session_id).all()
        rem_dicts = [
            {
                "file_name": r.session.files[0].filename if r.session and r.session.files else "File",
                "action_type": r.action_type,
                "proposed_details": r.proposed_details,
                "status": r.status
            }
            for r in rem_objs
        ]

        agent_objs = db.query(AgentExecution).filter(AgentExecution.session_id == session_id).all()
        agent_dicts = [
            {
                "agent_name": a.agent_name,
                "status": a.status,
                "execution_duration_ms": a.execution_duration_ms,
                "task_description": a.task_description
            }
            for a in agent_objs
        ]

        files_objs = session.files
        files_dicts = [
            {
                "filename": f.filename,
                "file_type": f.file_type,
                "file_size_bytes": f.file_size_bytes,
                "sensitivity_level": getattr(f, "sensitivity_level", "LOW") or "LOW",
                "findings_count": len([x for x in f.findings if x.classification in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"]]),
                "categories": list(set([x.entity_type for x in f.findings if x.classification in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"]])),
                "sample_locations": [x.location for x in f.findings if x.location][:3]
            }
            for f in files_objs
        ]

        session_data = {
            "id": session.id,
            "total_files": session.total_files,
            "total_findings": session.total_findings,
            "risk_score": session.risk_score,
            "critical_findings": session.critical_findings,
            "high_findings": session.high_findings,
            "medium_findings": session.medium_findings,
            "low_findings": session.low_findings,
            "ambiguous_findings": session.ambiguous_findings,
            "files": files_dicts,
            "findings": findings_dicts,
            "compliance_observations": obs_dicts,
            "remediation_actions": rem_dicts,
            "agent_executions": agent_dicts
        }

        return ReportService.generate_pdf_report(session_data)
