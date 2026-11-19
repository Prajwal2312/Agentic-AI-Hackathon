"""
Agent 4: DPDP Compliance Agent
Responsibilities:
- Map discovered personal data findings to India's DPDP Act, 2023 and DPDP Rules, 2025
- Identify potential compliance gaps without fabricating legal provisions
- Explain the statutory relevance of each provision
- Provide clear evidence supporting each observation
- Track commencement status (COMMENCED vs PHASED_COMMENCEMENT vs DRAFT_RULES_2025)
- Generate actionable compliance recommendations for Data Protection Officers
"""

import time
from typing import Dict, Any, List
from backend.app.agents.state import AgentState
from backend.app.engine.dpdp_kb import map_finding_to_dpdp_provisions

class ComplianceAgent:
    def __init__(self):
        self.name = "DPDP Compliance Agent"

    def run(self, state: AgentState) -> Dict[str, Any]:
        start_time = time.time()
        logs: List[str] = []
        logs.append(f"DPDP Compliance Agent started for session {state.session_id}.")
        logs.append("Querying DPDP Act 2023 & Rules 2025 verifiable knowledge base...")

        observations: List[Dict[str, Any]] = []
        seen_observations = set()

        for finding in state.findings:
            # Map each finding based on entity type, classification, and risk level
            mapped_provisions = map_finding_to_dpdp_provisions(
                entity_type=finding.entity_type,
                classification=finding.classification,
                risk_level=finding.risk_level,
                file_type=finding.file_name.split(".")[-1].upper() if "." in finding.file_name else "FILE"
            )

            for prov in mapped_provisions:
                obs_key = (prov["provision_section"], prov["observation"], finding.file_name)
                if obs_key not in seen_observations:
                    seen_observations.add(obs_key)
                    obs_entry = {
                        "finding_id": None,
                        "file_name": finding.file_name,
                        "provision_section": prov["provision_section"],
                        "provision_title": prov["provision_title"],
                        "status_in_force": prov["status_in_force"],
                        "observation": prov["observation"],
                        "evidence": f"File: {finding.file_name} ({finding.location}). Detected: {finding.entity_type} [{finding.masked_value}]. {prov['evidence']}",
                        "recommendation": prov["recommendation"],
                        "severity": prov["severity"]
                    }
                    observations.append(obs_entry)
                    logs.append(f"LEGAL MAPPING: {prov['provision_section']} applied to {finding.file_name} ({prov['severity']}).")

        duration_ms = int((time.time() - start_time) * 1000)
        logs.append(f"Compliance mapping completed in {duration_ms}ms. Generated {len(observations)} statutory observations.")

        return {
            "current_phase": "REMEDIATION_PLANNING",
            "compliance_observations": observations,
            "audit_logs": [{
                "agent_name": self.name,
                "action": "DPDP_COMPLIANCE_MAPPING_COMPLETED",
                "details": f"Generated {len(observations)} legal compliance observations across DPDP Act 2023 and 2025 Rules."
            }],
            "agent_executions": {
                self.name: {
                    "status": "COMPLETED",
                    "task_description": f"Mapped discovered PII items to Sections 4, 5, 6, 8(1), 8(5), 8(6), 8(7), 12 of DPDP Act 2023 and Rules 2025.",
                    "execution_duration_ms": duration_ms,
                    "findings_count": len(observations),
                    "logs": logs
                }
            }
        }
