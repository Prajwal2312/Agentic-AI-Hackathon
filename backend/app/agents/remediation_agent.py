"""
Agent 5: Remediation Agent
Responsibilities:
- Generate masked/redacted copies of documents containing personal data
- Recommend restricting file access permissions
- Identify files requiring statutory retention review under Section 8(7) DPDP Act
- Formulate remediation plans requiring human-in-the-loop administrator approval
- IMPORTANT: Never permanently delete or overwrite original files automatically
"""

import time
from pathlib import Path
from typing import Dict, Any, List
from backend.app.agents.state import AgentState
from backend.app.services.masking_service import MaskingService

class RemediationAgent:
    def __init__(self):
        self.name = "Remediation Agent"

    def run(self, state: AgentState) -> Dict[str, Any]:
        start_time = time.time()
        logs: List[str] = []
        logs.append(f"Remediation Agent initiated for session {state.session_id}.")
        logs.append("Formulating remediation actions and generating masked document copies...")

        remediation_actions: List[Dict[str, Any]] = []
        redacted_paths: List[str] = []

        # Group findings by file
        findings_by_file: Dict[str, List[Dict[str, Any]]] = {}
        for f in state.findings:
            f_dict = f.dict() if hasattr(f, "dict") else dict(f)
            findings_by_file.setdefault(f.file_name, []).append(f_dict)

        for inv in state.file_inventory:
            fname = inv["filename"]
            fpath = inv["file_path"]
            file_id = inv["file_id"]
            file_findings = findings_by_file.get(fname, [])

            # Filter confirmed/likely personal data
            pii_items = [
                f for f in file_findings
                if f.get("classification") in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"]
            ]

            if not pii_items:
                logs.append(f"File {fname} contains no exposed personal data. No redaction needed.")
                continue

            # 1. Action: Generate Redacted Copy
            logs.append(f"Generating masked/redacted copy for {fname} ({len(pii_items)} sensitive values)...")
            redacted_file = MaskingService.generate_redacted_copy(fpath, pii_items)
            redacted_paths.append(redacted_file)

            remediation_actions.append({
                "file_id": file_id,
                "file_name": fname,
                "action_type": "MASK_DOCUMENT",
                "status": "PENDING_APPROVAL",
                "original_file_path": fpath,
                "redacted_file_path": redacted_file,
                "has_redacted_copy": bool(redacted_file),
                "proposed_details": f"Generated cryptographic/masked copy replacing {len(pii_items)} plaintext personal identifiers while preserving non-personal structure.",
                "admin_notes": "Pending security officer review before distribution."
            })

            # 2. Action: Restrict Access
            remediation_actions.append({
                "file_id": file_id,
                "file_name": fname,
                "action_type": "RESTRICT_ACCESS",
                "status": "PENDING_APPROVAL",
                "original_file_path": fpath,
                "redacted_file_path": None,
                "has_redacted_copy": False,
                "proposed_details": f"Restrict read/write permissions on original file to authorized Data Protection Officers only (DPDP Section 8(5)).",
                "admin_notes": "Requires IT infrastructure approval."
            })

            # 3. Action: Retention Review if file is an export or backup
            if any(k in fname.lower() for k in ["export", "backup", "old", "archive", "temp"]):
                remediation_actions.append({
                    "file_id": file_id,
                    "file_name": fname,
                    "action_type": "RETENTION_REVIEW",
                    "status": "PENDING_APPROVAL",
                    "original_file_path": fpath,
                    "redacted_file_path": None,
                    "has_redacted_copy": False,
                    "proposed_details": f"File '{fname}' matches historical export pattern. Conduct retention audit under DPDP Section 8(7) to archive or securely purge.",
                    "admin_notes": "Subject to legal hold verification before erasure."
                })

        duration_ms = int((time.time() - start_time) * 1000)
        logs.append(f"Remediation plan generated in {duration_ms}ms with {len(remediation_actions)} actionable proposals. Human approval required.")

        return {
            "current_phase": "AUDIT_COMPLETED",
            "remediation_actions": remediation_actions,
            "redacted_files": redacted_paths,
            "audit_logs": [{
                "agent_name": self.name,
                "action": "REMEDIATION_PLAN_PROPOSED",
                "details": f"Generated {len(remediation_actions)} remediation actions across {len(state.file_inventory)} files. Original files preserved intact."
            }],
            "agent_executions": {
                self.name: {
                    "status": "COMPLETED",
                    "task_description": f"Created masked copies and prepared access control/retention proposals for human review.",
                    "execution_duration_ms": duration_ms,
                    "findings_count": len(remediation_actions),
                    "logs": logs
                }
            }
        }
