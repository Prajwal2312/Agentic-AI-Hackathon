"""
Curated knowledge base for India's Digital Personal Data Protection Act, 2023 (DPDP Act)
and the Digital Personal Data Protection Rules, 2025.
Contains verifiable legal provisions, commencement status, penalties, and compliance requirements.
"""

from typing import List, Dict, Any, Optional

DPDP_PROVISIONS = {
    "SEC_4_GROUNDS": {
        "section": "Section 4",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Grounds for Processing Personal Data",
        "status_in_force": "COMMENCED",
        "summary": "Personal data may only be processed for a lawful purpose for which the Data Principal has given consent or for certain legitimate uses.",
        "max_penalty_inr": "50 Crores",
        "guidance": "Processing unconsented or obsolete personal records across shared drives violates the lawful purpose principle.",
        "recommendation": "Identify valid legal ground (consent or legitimate use) for each repository holding personal data."
    },
    "SEC_5_NOTICE": {
        "section": "Section 5",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Notice Requirement before or at the time of Consent",
        "status_in_force": "COMMENCED",
        "summary": "Data Fiduciary must give itemised notice in clear and plain language detailing the personal data sought, specific purpose, manner of exercising rights, and grievance officer contact.",
        "max_penalty_inr": "50 Crores",
        "guidance": "Personal data collected in unstructured forms without verifiable notice logs presents significant audit liability.",
        "recommendation": "Review data collection forms and align data categories stored with published privacy notices."
    },
    "SEC_6_CONSENT": {
        "section": "Section 6",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Consent Architecture and Withdrawal",
        "status_in_force": "COMMENCED",
        "summary": "Consent must be free, specific, informed, unconditional, and unambiguous with clear affirmative action. Data Principal has right to withdraw consent easily.",
        "max_penalty_inr": "50 Crores",
        "guidance": "Unlinked legacy records prevent timely execution of consent withdrawal requests.",
        "recommendation": "Tag customer identifiers to consent logs to enable programmatic withdrawal or restriction."
    },
    "SEC_8_1_ACCURACY": {
        "section": "Section 8(1)",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Obligation of Data Accuracy and Completeness",
        "status_in_force": "COMMENCED",
        "summary": "Data Fiduciary must ensure personal data processed is accurate, complete, and consistent if used to make a decision affecting the Data Principal or disclosed to another Data Fiduciary.",
        "max_penalty_inr": "100 Crores",
        "guidance": "Stale customer files, duplicate records, and untracked exports pose high risk of inaccurate downstream processing.",
        "recommendation": "Implement data reconciliation to deprecate untracked manual exports."
    },
    "SEC_8_5_SECURITY": {
        "section": "Section 8(5)",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Reasonable Security Safeguards to Prevent Personal Data Breach",
        "status_in_force": "COMMENCED",
        "summary": "Data Fiduciary must protect personal data in its possession or under its control by taking reasonable security safeguards to prevent personal data breach.",
        "max_penalty_inr": "250 Crores (Schedule 1)",
        "guidance": "Storing unencrypted plaintext PAN, Aadhaar, Bank Details, and Phone numbers in accessible folders or old exports fails the reasonable security safeguards test.",
        "recommendation": "Immediately redact or apply cryptographic access controls to files containing unmasked financial and government identifiers."
    },
    "SEC_8_6_BREACH_NOTIFICATION": {
        "section": "Section 8(6)",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Personal Data Breach Notification",
        "status_in_force": "COMMENCED",
        "summary": "In the event of a personal data breach, Data Fiduciary must give intimation of such breach to the Data Protection Board of India and each affected Data Principal in prescribed form and manner.",
        "max_penalty_inr": "200 Crores (Schedule 1)",
        "guidance": "Unmonitored shared folders leave organisations blind to exfiltration, precluding timely statutory notification.",
        "recommendation": "Establish continuous automated audit monitoring on sensitive document directories."
    },
    "SEC_8_7_STORAGE_LIMITATION": {
        "section": "Section 8(7)",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Data Erasure and Retention Limitation",
        "status_in_force": "COMMENCED",
        "summary": "Data Fiduciary must erase personal data upon Data Principal withdrawing consent or as soon as it is reasonable to assume that the specified purpose is no longer being served, unless retention is required under statutory law.",
        "max_penalty_inr": "100 Crores",
        "guidance": "Archived backups, abandoned employee resumes, and old exports retained indefinitely violate statutory retention caps.",
        "recommendation": "Enforce automated retention schedules to archive or securely shred unneeded historical files."
    },
    "SEC_9_CHILD_DATA": {
        "section": "Section 9",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Processing of Personal Data of Children",
        "status_in_force": "PHASED_COMMENCEMENT",
        "summary": "Requires verifiable parental consent prior to processing child personal data. Strict prohibition on behavioural monitoring, tracking, or targeted advertising directed at children.",
        "max_penalty_inr": "200 Crores (Schedule 1)",
        "guidance": "Identification of student, minor, or dependent records requires special parental verification flags.",
        "recommendation": "Segregate minor records and verify parental consent workflows."
    },
    "SEC_12_ERASURE_RIGHT": {
        "section": "Section 12",
        "act": "Digital Personal Data Protection Act, 2023",
        "title": "Right to Correction, Completion, Updating, and Erasure",
        "status_in_force": "COMMENCED",
        "summary": "A Data Principal has the right to correction of inaccurate personal data, completion of incomplete data, updating, and erasure of personal data that is no longer necessary.",
        "max_penalty_inr": "50 Crores",
        "guidance": "Untracked files across departments make fulfillment of erasure requests impossible, generating non-compliance.",
        "recommendation": "Maintain a centralised data discovery index to trace and execute erasure requests comprehensively."
    },
    "RULES_2025_SAFEGUARDS": {
        "section": "DPDP Rules 2025 (Draft/Commencing)",
        "act": "Digital Personal Data Protection Rules, 2025",
        "title": "Technical and Organisational Safeguards Specification",
        "status_in_force": "DRAFT_RULES_2025",
        "summary": "Mandates automated pseudonymisation, role-based access control, periodic vulnerability scans, and strict logging of document access containing PII.",
        "max_penalty_inr": "Regulatory Notice",
        "guidance": "Manual review of documents is non-compliant with continuous audit expectations under the 2025 Rules.",
        "recommendation": "Deploy agentic automated privacy scanners and automated masking pipelines."
    }
}

def map_finding_to_dpdp_provisions(
    entity_type: str,
    classification: str,
    risk_level: str,
    file_type: str
) -> List[Dict[str, Any]]:
    """
    Deterministically and contextually maps discovered PII findings
    to relevant legal provisions of DPDP Act 2023 and Rules 2025.
    Never fabricates legal provisions.
    """
    mapped: List[Dict[str, Any]] = []

    # If it is confirmed or likely personal data
    if classification in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"]:
        # Reasonable security safeguards applies to all personal data
        sec8_5 = DPDP_PROVISIONS["SEC_8_5_SECURITY"]
        mapped.append({
            "provision_section": f"{sec8_5['section']} - {sec8_5['act']}",
            "provision_title": sec8_5["title"],
            "status_in_force": sec8_5["status_in_force"],
            "observation": f"Unprotected {entity_type} discovered in {file_type} document requires reasonable security safeguards.",
            "evidence": f"Detected personal identifier ({entity_type}) with risk rating {risk_level}.",
            "recommendation": sec8_5["recommendation"],
            "severity": "CRITICAL" if risk_level == "CRITICAL" else ("HIGH" if risk_level == "HIGH" else "MEDIUM")
        })

        # Storage limitation observation
        sec8_7 = DPDP_PROVISIONS["SEC_8_7_STORAGE_LIMITATION"]
        mapped.append({
            "provision_section": f"{sec8_7['section']} - {sec8_7['act']}",
            "provision_title": sec8_7["title"],
            "status_in_force": sec8_7["status_in_force"],
            "observation": f"Ensure active legitimate business purpose or statutory retention mandate justifies holding this {entity_type} record.",
            "evidence": f"File contains individual personal data records without automated retention tags.",
            "recommendation": sec8_7["recommendation"],
            "severity": "MEDIUM"
        })

        # If sensitive government or financial identifier (Aadhaar, PAN, Bank details)
        if entity_type in ["AADHAAR", "PAN", "BANK_ACC", "CREDIT_CARD"]:
            rules = DPDP_PROVISIONS["RULES_2025_SAFEGUARDS"]
            mapped.append({
                "provision_section": f"{rules['section']} - {rules['act']}",
                "provision_title": rules["title"],
                "status_in_force": rules["status_in_force"],
                "observation": f"High sensitivity financial/statutory identifier ({entity_type}) must be masked or tokenized at rest.",
                "evidence": f"Plaintext {entity_type} finding detected with high exposure vulnerability.",
                "recommendation": "Deploy redaction or tokenization before sharing or archiving.",
                "severity": "HIGH"
            })

        # Right to Erasure / Data accuracy
        sec12 = DPDP_PROVISIONS["SEC_12_ERASURE_RIGHT"]
        mapped.append({
            "provision_section": f"{sec12['section']} - {sec12['act']}",
            "provision_title": sec12["title"],
            "status_in_force": sec12["status_in_force"],
            "observation": "File repository must be catalogued in the central Data Inventory to allow fulfillment of Data Principal access and erasure requests.",
            "evidence": f"Document indexed with personal identity fields ({entity_type}).",
            "recommendation": sec12["recommendation"],
            "severity": "LOW"
        })

    elif classification == "AMBIGUOUS":
        # Ambiguity requires human-in-the-loop review to prevent misclassification
        sec8_1 = DPDP_PROVISIONS["SEC_8_1_ACCURACY"]
        mapped.append({
            "provision_section": f"{sec8_1['section']} - {sec8_1['act']}",
            "provision_title": sec8_1["title"],
            "status_in_force": sec8_1["status_in_force"],
            "observation": "Ambiguous identifier requires verification to ensure organization records maintain accuracy and data classification integrity.",
            "evidence": f"Entity candidate with indeterminate personal vs system identifier status.",
            "recommendation": "Perform Human-in-the-loop verification to confirm data taxonomy.",
            "severity": "LOW"
        })

    return mapped
