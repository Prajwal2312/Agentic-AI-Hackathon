"""
Agent 2: Context Intelligence Agent
Responsibilities:
- Examine discovered fields, column labels, nearby text, and file structures
- Distinguish genuine personal data from non-personal operational identifiers
  (e.g., Order ID: 9876543210 vs Mobile Number: 9876543210)
- Classify findings into:
  - Confirmed personal data
  - Likely personal data
  - Non-personal identifiers
  - Ambiguous values
- Produce masked values, confidence scores, and evidence-based explanations
- Trigger human/LLM verification branch if confidence is ambiguous
"""

import time
import re
from typing import Dict, Any, List
from backend.app.agents.state import AgentState, AgentFinding
from backend.app.engine.context_classifier import context_engine
from backend.app.engine.pii_rules import (
    mask_value, RE_EMAIL, RE_INDIAN_MOBILE_STRICT, RE_GENERIC_10_DIGIT,
    RE_PAN, RE_AADHAAR, RE_BANK_ACCOUNT, extract_phone_digits, is_person_name_candidate
)

class ContextAgent:
    def __init__(self):
        self.name = "Context Intelligence Agent"

    def run(self, state: AgentState) -> Dict[str, Any]:
        start_time = time.time()
        logs: List[str] = []
        logs.append(f"Context Intelligence Agent activated for session {state.session_id}.")
        logs.append(f"Analyzing {len(state.discovered_records)} extracted field candidates...")

        findings: List[AgentFinding] = []
        ambiguous_candidates: List[Dict[str, Any]] = []

        for rec in state.discovered_records:
            val = str(rec["value"]).strip()
            col = str(rec.get("column_name", "")).strip()
            surrounding = str(rec.get("surrounding_text", "")).strip()
            doc_type = str(rec.get("document_type", "")).strip()
            loc_desc = str(rec.get("location_desc", "")).strip()
            file_id = rec.get("file_id", 1)
            file_name = rec.get("file_name", "document")

            # Candidate identification filter: check for Email, Phone, Name, PAN, Aadhaar, Account, or semantic headers
            is_candidate = False
            candidate_hint = None

            hint_from_rec = rec.get("entity_hint")
            phone_found = extract_phone_digits(val)

            if hint_from_rec:
                is_candidate = True
                candidate_hint = hint_from_rec
            elif "@" in val and "." in val:
                is_candidate = True
                candidate_hint = "EMAIL"
            elif phone_found:
                is_candidate = True
                candidate_hint = "PHONE"
            elif is_person_name_candidate(val):
                is_candidate = True
                candidate_hint = "PERSON_NAME"
            elif RE_PAN.search(val):
                is_candidate = True
                candidate_hint = "PAN"
            elif RE_AADHAAR.search(val):
                is_candidate = True
                candidate_hint = "AADHAAR"
            elif re.search(r'\d{9,18}', re.sub(r'\D', '', val)):
                is_candidate = True
                candidate_hint = "NUMERIC_ID"
            elif any(k in col.lower() for k in ["name", "email", "phone", "mobile", "pan", "aadhaar", "aadhar", "account", "order", "txn", "id", "cust", "emp", "user", "applicant"]):
                is_candidate = True
                candidate_hint = "HEADER_MATCH"

            if not is_candidate:
                continue

            # Execute Context Classification Engine
            result = context_engine.classify_candidate(
                value=val,
                column_name=col,
                document_type=doc_type,
                surrounding_text=surrounding,
                candidate_entity_type=candidate_hint
            )

            classification = result["classification"]
            confidence = result["confidence"]
            reason = result["reason"]
            entity_type = result["entity_type"]

            # Mask value
            masked = mask_value(val, entity_type)

            finding = AgentFinding(
                file_id=file_id,
                file_name=file_name,
                entity_type=entity_type,
                raw_value=val,
                masked_value=masked,
                location=loc_desc,
                row_idx=rec.get("row_idx"),
                col_name=col,
                page_number=rec.get("page_number"),
                classification=classification,
                confidence=confidence,
                risk_level="LOW",  # Will be assessed by Risk Agent
                explanation=reason,
                detection_method="CONTEXT_INTELLIGENCE_ENGINE",
                surrounding_context=surrounding[:200],
                is_ambiguous=(classification == "AMBIGUOUS"),
                verified_by_context=(classification != "AMBIGUOUS")
            )

            findings.append(finding)

            if classification == "AMBIGUOUS":
                ambiguous_candidates.append({
                    "file_name": file_name,
                    "value": masked,
                    "column_name": col,
                    "location": loc_desc,
                    "confidence": confidence
                })
                logs.append(f"FLAGGED AMBIGUOUS: Value '{masked}' in '{col}' ({loc_desc}) requires extra verification.")
            elif classification == "NON_PERSONAL_IDENTIFIER":
                logs.append(f"DISPROVED FALSE POSITIVE: Value '{masked}' in '{col}' resolved as {entity_type} (Non-personal identifier).")
            else:
                logs.append(f"CONFIRMED PII: '{masked}' identified as {entity_type} ({classification}, confidence {confidence:.2f}).")

        duration_ms = int((time.time() - start_time) * 1000)
        needs_extra = len(ambiguous_candidates) > 0

        logs.append(f"Contextual analysis finished in {duration_ms}ms. Found {len(findings)} evaluated items ({len(ambiguous_candidates)} ambiguous).")

        return {
            "current_phase": "VERIFY_OR_ASSESS",
            "findings": findings,
            "ambiguous_candidates": ambiguous_candidates,
            "needs_extra_verification": needs_extra,
            "audit_logs": [{
                "agent_name": self.name,
                "action": "CONTEXT_ANALYSIS_COMPLETED",
                "details": f"Classified {len(findings)} candidate fields with context verification. Disproved false positives and isolated {len(ambiguous_candidates)} ambiguous values."
            }],
            "agent_executions": {
                self.name: {
                    "status": "COMPLETED",
                    "task_description": f"Applied context intelligence to classify {len(findings)} candidate fields across document structure and headers.",
                    "execution_duration_ms": duration_ms,
                    "findings_count": len(findings),
                    "logs": logs
                }
            }
        }
