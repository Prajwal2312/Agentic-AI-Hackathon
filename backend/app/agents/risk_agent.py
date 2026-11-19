"""
Agent 3: Risk Assessment Agent
Responsibilities:
- Evaluate sensitivity of personal data types (Aadhaar, PAN, Bank Details vs Phone, Email)
- Factor in record volume, file location exposure, and unencrypted status
- Compute configurable risk score (0-100) and assign risk categories:
  - CRITICAL (80-100)
  - HIGH (60-79)
  - MEDIUM (40-59)
  - LOW (0-39)
- Provide clear risk rationales without falsely equating presence of PII alone with a legal violation
"""

import time
from typing import Dict, Any, List
from backend.app.agents.state import AgentState

# Sensitivity Weights (Base Score out of 50)
SENSITIVITY_WEIGHTS = {
    "AADHAAR": 45.0,        # Statutory identity document
    "BANK_ACC": 45.0,       # Financial data
    "CREDIT_CARD": 48.0,    # High direct fraud impact
    "PAN": 38.0,            # National tax identifier
    "PHONE": 25.0,          # Contact information
    "EMAIL": 20.0,          # Contact information
    "PERSON_NAME": 15.0,    # Natural person name
    "AMBIGUOUS_NUMERIC_10": 10.0,
    "SYSTEM_IDENTIFIER": 0.0,
    "GENERAL_DATA": 0.0
}

class RiskAgent:
    def __init__(self):
        self.name = "Risk Assessment Agent"

    def run(self, state: AgentState) -> Dict[str, Any]:
        start_time = time.time()
        logs: List[str] = []
        logs.append(f"Risk Assessment Agent started for session {state.session_id}.")

        risk_assessments: List[Dict[str, Any]] = []
        risk_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        total_personal_score = 0.0
        personal_count = 0

        # Assess exposure factors from file inventory
        file_counts: Dict[str, int] = {}
        for f in state.findings:
            file_counts[f.file_name] = file_counts.get(f.file_name, 0) + 1

        for finding in state.findings:
            entity = finding.entity_type
            classification = finding.classification
            f_name = finding.file_name

            # 1. Non-personal identifiers have negligible risk
            if classification == "NON_PERSONAL_IDENTIFIER":
                finding.risk_level = "LOW"
                finding.risk_score = 5.0
                risk_dist["LOW"] += 1
                risk_assessments.append({
                    "finding_id": None,
                    "risk_score": 5.0,
                    "risk_category": "LOW",
                    "sensitivity_factor": 0.1,
                    "volume_factor": 1.0,
                    "exposure_factor": 1.0,
                    "rationale": f"Verified as non-personal operational identifier ({entity}). Negligible privacy risk."
                })
                continue

            # 2. Base sensitivity score
            base_score = SENSITIVITY_WEIGHTS.get(entity, 20.0)

            # 3. Volume Factor: Files with many records represent higher aggregation risk
            records_in_file = file_counts.get(f_name, 1)
            if records_in_file > 50:
                volume_multiplier = 1.3
            elif records_in_file > 10:
                volume_multiplier = 1.15
            else:
                volume_multiplier = 1.0

            # 4. Exposure Factor: File type and storage vulnerability
            exposure_multiplier = 1.0
            if "export" in f_name.lower() or "backup" in f_name.lower() or "old" in f_name.lower():
                exposure_multiplier = 1.25  # High unmonitored exposure
            elif f_name.lower().endswith(".csv") or f_name.lower().endswith(".xlsx"):
                exposure_multiplier = 1.1   # Easily forwardable spreadsheet

            # Compute combined risk score (capped at 100)
            score = min(100.0, base_score * volume_multiplier * exposure_multiplier)

            # Assign category
            if score >= 80.0:
                cat = "CRITICAL"
            elif score >= 60.0:
                cat = "HIGH"
            elif score >= 40.0:
                cat = "MEDIUM"
            else:
                cat = "LOW"

            finding.risk_level = cat
            finding.risk_score = round(score, 1)
            risk_dist[cat] += 1
            total_personal_score += score
            personal_count += 1

            rationale = (
                f"Discovered {entity} classified as {classification}. "
                f"Base sensitivity weight ({base_score}) adjusted for file record density ({records_in_file} records) "
                f"and storage exposure factor ({exposure_multiplier:.2f}x). Potential unauthorized exposure impact: {cat}."
            )

            risk_assessments.append({
                "finding_id": None,
                "risk_score": round(score, 1),
                "risk_category": cat,
                "sensitivity_factor": base_score / 50.0,
                "volume_factor": volume_multiplier,
                "exposure_factor": exposure_multiplier,
                "rationale": rationale
            })

            if cat in ["CRITICAL", "HIGH"]:
                logs.append(f"HIGH RISK ALERT: {entity} ({finding.masked_value}) in {f_name} scored {score:.1f} ({cat}).")

        # Overall session risk score
        overall_score = round(total_personal_score / max(personal_count, 1), 1) if personal_count > 0 else 10.0
        
        # Calculate file sensitivity classification
        file_sensitivity: Dict[str, str] = {}
        for f in state.findings:
            if f.classification in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"]:
                current = file_sensitivity.get(f.file_name, "LOW")
                if f.risk_level == "CRITICAL" or current == "CRITICAL":
                    file_sensitivity[f.file_name] = "CRITICAL"
                elif f.risk_level == "HIGH" or current == "HIGH":
                    file_sensitivity[f.file_name] = "HIGH"
                elif f.risk_level == "MEDIUM" or current == "MEDIUM":
                    file_sensitivity[f.file_name] = "MEDIUM"
                else:
                    file_sensitivity[f.file_name] = "LOW"
            else:
                if f.file_name not in file_sensitivity:
                    file_sensitivity[f.file_name] = "LOW"

        duration_ms = int((time.time() - start_time) * 1000)
        logs.append(f"Risk assessment finalized in {duration_ms}ms. Overall Score: {overall_score}/100. Severity Profile: {risk_dist}")

        return {
            "current_phase": "COMPLIANCE_EVALUATION",
            "overall_risk_score": overall_score,
            "risk_distribution": risk_dist,
            "risk_assessments": risk_assessments,
            "file_sensitivity": file_sensitivity,
            "audit_logs": [{
                "agent_name": self.name,
                "action": "RISK_ASSESSMENT_COMPLETED",
                "details": f"Calculated composite privacy risk score ({overall_score}/100). Critical: {risk_dist['CRITICAL']}, High: {risk_dist['HIGH']}, Medium: {risk_dist['MEDIUM']}, Low: {risk_dist['LOW']}."
            }],
            "agent_executions": {
                self.name: {
                    "status": "COMPLETED",
                    "task_description": f"Evaluated privacy exposure, sensitivity multipliers, and aggregation impact across {len(state.findings)} findings.",
                    "execution_duration_ms": duration_ms,
                    "findings_count": len(risk_assessments),
                    "logs": logs
                }
            }
        }
