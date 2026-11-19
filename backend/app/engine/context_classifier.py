"""
Context Intelligence Classification Engine.
The primary differentiator of PRIVESCAN AI.
Distinguishes genuine personal data from values that only resemble personal information
(e.g., 10-digit Order IDs vs 10-digit Mobile numbers, Transaction IDs vs Bank Accounts).

Evaluates:
- Column headers & field labels
- Surrounding textual context
- Document structure & type
- Relationships with neighbouring fields
- Algorithmic & deterministic validation
- Optional LLM-based reasoning (Gemini API) for ambiguous cases
"""

import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from backend.app.config import settings
from backend.app.engine.pii_rules import (
    validate_pan, validate_aadhaar_verhoeff, RE_EMAIL, RE_GENERIC_10_DIGIT,
    extract_phone_digits, is_person_name_candidate
)

logger = logging.getLogger(__name__)

# Semantic header sets
NON_PERSONAL_HEADERS = {
    "order_id", "order_number", "order_no", "orderid", "orderno",
    "invoice_id", "invoice_number", "invoice_no", "inv_no", "bill_no",
    "transaction_id", "txn_id", "txnid", "payment_reference", "ref_no",
    "tracking_id", "tracking_number", "awb_number", "consignment_no",
    "product_id", "product_code", "sku", "item_code", "part_number",
    "serial_number", "sr_no", "batch_no", "lot_number", "container_id",
    "session_id", "device_id", "machine_id", "terminal_id", "ip_address",
    "ticket_id", "case_number", "issue_key", "claim_id"
}

PHONE_HEADERS = {
    "phone", "phone_number", "phone_no", "phoneno", "mobile", "mobile_number",
    "mobile_no", "mobileno", "contact", "contact_number", "contact_no",
    "cell", "cellphone", "telephone", "tel_no", "whatsapp", "sms_number",
    "cust_phone", "cust_mobile", "user_phone", "employee_phone", "emergency_contact"
}

EMAIL_HEADERS = {
    "email", "email_address", "email_id", "mail", "contact_email",
    "cust_email", "user_email", "employee_email", "official_email", "personal_email"
}

GOVT_ID_HEADERS = {
    "pan", "pan_number", "pan_card", "pan_no", "tax_id",
    "aadhaar", "aadhaar_number", "aadhaar_no", "uidai", "aadhar", "national_id",
    "voter_id", "passport", "passport_no", "driving_license", "dl_no"
}

FINANCIAL_HEADERS = {
    "bank_account", "account_number", "acc_no", "account_no", "bank_acc",
    "ifsc", "ifsc_code", "credit_card", "debit_card", "card_number", "cvv"
}

NAME_HEADERS = {
    "name", "full_name", "first_name", "last_name", "customer_name",
    "employee_name", "user_name", "patient_name", "candidate_name", "holder_name",
    "applicant", "applicant_name", "contact_person", "person", "client",
    "client_name", "doctor", "beneficiary", "student", "individual"
}

def normalize_header(header: str) -> str:
    """Normalizes header string for semantic matching."""
    if not header:
        return ""
    clean = header.lower().strip()
    clean = clean.replace("-", "_").replace(" ", "_").replace(".", "_")
    return clean

class ContextIntelligenceEngine:
    def __init__(self):
        self.gemini_client = None
        self._init_gemini()

    def _init_gemini(self):
        """Initializes Gemini API client if key is configured."""
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini API: {e}. Falling back to contextual rule engine.")

    def classify_candidate(
        self,
        value: str,
        column_name: Optional[str] = "",
        document_type: Optional[str] = "",
        surrounding_text: Optional[str] = "",
        candidate_entity_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classifies an extracted value using multi-layered contextual analysis.
        Returns:
            classification: CONFIRMED_PERSONAL_DATA | LIKELY_PERSONAL_DATA | NON_PERSONAL_IDENTIFIER | AMBIGUOUS
            confidence: float (0.0 to 1.0)
            reason: str
            entity_type: str
            is_personal_data: bool
        """
        val_str = str(value).strip()
        header_norm = normalize_header(column_name)
        text_context = (surrounding_text or "").lower()
        doc_type_norm = (document_type or "").lower()

        # Step 1: Explicit Non-Personal Identifier Headers
        # (e.g. Order_ID: 9876543210 vs Mobile: 9876543210)
        for non_p in NON_PERSONAL_HEADERS:
            if non_p in header_norm:
                return {
                    "classification": "NON_PERSONAL_IDENTIFIER",
                    "confidence": 0.98,
                    "reason": f"Column header '{column_name}' conclusively indicates an operational or system identifier ({non_p}), not personal data.",
                    "entity_type": "SYSTEM_IDENTIFIER",
                    "is_personal_data": False
                }

        # Step 2: Check surrounding text for strong non-personal clues
        non_personal_keywords = [
            "order #", "order id", "invoice #", "tracking code", "item sku",
            "transaction reference", "consignment no", "ticket ref"
        ]
        for kw in non_personal_keywords:
            if kw in text_context and not any(p in header_norm for p in PHONE_HEADERS):
                return {
                    "classification": "NON_PERSONAL_IDENTIFIER",
                    "confidence": 0.94,
                    "reason": f"Surrounding context contains non-personal prefix '{kw}', identifying this numerical sequence as an operational reference.",
                    "entity_type": "SYSTEM_IDENTIFIER",
                    "is_personal_data": False
                }

        # Step 3: Strong Phone / Mobile indicators
        phone_digits = extract_phone_digits(val_str)
        has_phone_header = any(p in header_norm for p in PHONE_HEADERS)
        if phone_digits or has_phone_header or candidate_entity_type == "PHONE":
            if phone_digits:
                first_digit = phone_digits[0]
                return {
                    "classification": "CONFIRMED_PERSONAL_DATA",
                    "confidence": 0.98 if has_phone_header else 0.95,
                    "reason": f"Valid 10-digit mobile number ({phone_digits[:2]}******{phone_digits[-2:]}) matching Indian telecommunication allocation series {first_digit}xxxxxxxxx.",
                    "entity_type": "PHONE",
                    "is_personal_data": True
                }
            else:
                digits_only = "".join(filter(str.isdigit, val_str))
                if 7 <= len(digits_only) <= 15:
                    return {
                        "classification": "LIKELY_PERSONAL_DATA",
                        "confidence": 0.91,
                        "reason": f"The column header '{column_name}' and numeric sequence ({val_str}) indicate contact telephone details.",
                        "entity_type": "PHONE",
                        "is_personal_data": True
                    }

        # Step 4: Email validation and header analysis
        if RE_EMAIL.match(val_str) or any(e in header_norm for e in EMAIL_HEADERS):
            if "@" in val_str:
                # Check if it is a generic system email vs personal email
                lower_val = val_str.lower()
                if any(x in lower_val for x in ["noreply", "no-reply", "support@", "admin@", "billing@", "sales@"]):
                    return {
                        "classification": "NON_PERSONAL_IDENTIFIER",
                        "confidence": 0.92,
                        "reason": f"The email '{val_str}' is an organizational role-based functional mailbox, not an individual's personal data.",
                        "entity_type": "FUNCTIONAL_EMAIL",
                        "is_personal_data": False
                    }
                return {
                    "classification": "CONFIRMED_PERSONAL_DATA",
                    "confidence": 0.99,
                    "reason": f"Conforms to RFC email specification and header/context represents an identifiable natural person's email address.",
                    "entity_type": "EMAIL",
                    "is_personal_data": True
                }

        # Step 5: Indian PAN Card validation
        clean_pan = val_str.strip().upper()
        is_pan_format = bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', clean_pan))
        has_pan_header = any(g in header_norm for g in ["pan", "tax_id"])
        if is_pan_format or has_pan_header or candidate_entity_type == "PAN":
            if is_pan_format:
                fourth = clean_pan[3]
                if fourth == 'P':
                    return {
                        "classification": "CONFIRMED_PERSONAL_DATA",
                        "confidence": 0.99,
                        "reason": f"PAN structure '{clean_pan[:2]}***{clean_pan[-1]}' conforms to Indian Income Tax format with 4th character 'P' signifying an Individual Person.",
                        "entity_type": "PAN",
                        "is_personal_data": True
                    }
                elif fourth in 'CHFATBLJG':
                    return {
                        "classification": "LIKELY_PERSONAL_DATA",
                        "confidence": 0.85,
                        "reason": f"Valid PAN format '{clean_pan[:2]}***{clean_pan[-1]}' with 4th character '{fourth}' signifying a non-individual entity (Company/Trust/Firm).",
                        "entity_type": "PAN_ORGANIZATION",
                        "is_personal_data": False
                    }
                else:
                    return {
                        "classification": "CONFIRMED_PERSONAL_DATA" if has_pan_header else "LIKELY_PERSONAL_DATA",
                        "confidence": 0.95 if has_pan_header else 0.90,
                        "reason": f"Alphanumeric structure '{clean_pan[:2]}***{clean_pan[-1]}' matches Indian PAN pattern under '{column_name or 'Tax Identifier'}'.",
                        "entity_type": "PAN",
                        "is_personal_data": True
                    }
            elif has_pan_header and len(clean_pan) == 10:
                return {
                    "classification": "CONFIRMED_PERSONAL_DATA",
                    "confidence": 0.92,
                    "reason": f"10-character code under PAN header '{column_name}' identified as tax personal identifier.",
                    "entity_type": "PAN",
                    "is_personal_data": True
                }

        # Step 6: Indian Aadhaar validation
        digits_aadhaar = "".join(filter(str.isdigit, val_str))
        is_aadhaar_pattern = (
            (len(digits_aadhaar) == 12 and (
                bool(re.match(r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}$', val_str.strip())) or
                any(a in header_norm for a in ["aadhaar", "aadhar", "uidai"]) or
                candidate_entity_type == "AADHAAR"
            ))
        )
        if is_aadhaar_pattern:
            is_valid_chk = validate_aadhaar_verhoeff(digits_aadhaar)
            return {
                "classification": "CONFIRMED_PERSONAL_DATA",
                "confidence": 0.99 if is_valid_chk else 0.94,
                "reason": f"12-digit Indian National Identity Number (Aadhaar). {'Verified with Verhoeff algorithmic checksum.' if is_valid_chk else 'Matches standard 12-digit UIDAI structure.'}",
                "entity_type": "AADHAAR",
                "is_personal_data": True
            }

        # Step 7: Bank Account details
        if any(b in header_norm for b in FINANCIAL_HEADERS) or candidate_entity_type == "BANK_ACC":
            digits_bank = "".join(filter(str.isdigit, val_str))
            if 9 <= len(digits_bank) <= 18:
                return {
                    "classification": "CONFIRMED_PERSONAL_DATA",
                    "confidence": 0.95,
                    "reason": f"Header '{column_name}' and numeric sequence of {len(digits_bank)} digits matches financial bank account format.",
                    "entity_type": "BANK_ACC",
                    "is_personal_data": True
                }

        # Step 8: Person Names
        has_name_header = any(n in header_norm for n in NAME_HEADERS)
        if has_name_header or candidate_entity_type == "PERSON_NAME" or is_person_name_candidate(val_str):
            if is_person_name_candidate(val_str) or has_name_header:
                return {
                    "classification": "CONFIRMED_PERSONAL_DATA",
                    "confidence": 0.96 if has_name_header else 0.92,
                    "reason": f"Value '{val_str}' identified as natural person name (capitalized personal name tokens) under '{column_name or 'Document Text'}'.",
                    "entity_type": "PERSON_NAME",
                    "is_personal_data": True
                }

        # Step 9: Ambiguous 10-digit number without explicit header
        digits = "".join(filter(str.isdigit, val_str))
        if len(digits) == 10:
            # Check if LLM is available for verification of ambiguous candidate
            if self.gemini_client:
                llm_result = self._classify_with_llm(val_str, column_name, document_type, surrounding_text)
                if llm_result:
                    return llm_result

            # Deterministic Fallback for ambiguous 10-digit candidate:
            # If start with 6-9 in customer context, likely phone; otherwise ambiguous
            if digits[0] in "6789" and any(k in doc_type_norm for k in ["customer", "employee", "user", "contact"]):
                return {
                    "classification": "LIKELY_PERSONAL_DATA",
                    "confidence": 0.72,
                    "reason": f"10-digit sequence beginning with mobile prefix '{digits[0]}' in '{document_type}' context, though column header is non-standard.",
                    "entity_type": "PHONE",
                    "is_personal_data": True
                }
            else:
                return {
                    "classification": "AMBIGUOUS",
                    "confidence": 0.50,
                    "reason": f"10-digit numerical sequence '{val_str}' lacks conclusive semantic metadata (could be an Order ID, Serial Number, or Phone number). Flagged for human review.",
                    "entity_type": "AMBIGUOUS_NUMERIC_10",
                    "is_personal_data": False
                }

        # Default fallback
        return {
            "classification": "NON_PERSONAL_IDENTIFIER",
            "confidence": 0.80,
            "reason": f"No personal data indicators or matching PII semantic signatures identified for header '{column_name}'.",
            "entity_type": "GENERAL_DATA",
            "is_personal_data": False
        }

    def _classify_with_llm(
        self,
        value: str,
        column_name: str,
        document_type: str,
        surrounding_text: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes Gemini LLM for structured semantic reasoning on ambiguous cases."""
        try:
            prompt = f"""
You are an expert AI data privacy auditor for India's DPDP Act, 2023.
Analyze this ambiguous candidate value and determine whether it represents genuine personal data or a non-personal system identifier (such as an Order ID, Transaction ID, SKU, or tracking code).

Candidate details:
- Value: {value}
- Column Header: {column_name}
- Document Type: {document_type}
- Surrounding Context: {surrounding_text}

Respond strictly with a JSON object adhering to this schema:
{{
  "classification": "CONFIRMED_PERSONAL_DATA" | "LIKELY_PERSONAL_DATA" | "NON_PERSONAL_IDENTIFIER" | "AMBIGUOUS",
  "confidence": <float between 0.0 and 1.0>,
  "reason": "<clear explanation of why this is or is not personal data based on context>",
  "entity_type": "<e.g., PHONE, ORDER_ID, TRANSACTION_ID, AADHAAR, PAN, BANK_ACC, etc.>",
  "is_personal_data": <boolean>
}}
"""
            response = self.gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            return {
                "classification": data.get("classification", "AMBIGUOUS"),
                "confidence": float(data.get("confidence", 0.75)),
                "reason": data.get("reason", "Classified via Gemini contextual reasoning."),
                "entity_type": data.get("entity_type", "UNKNOWN"),
                "is_personal_data": bool(data.get("is_personal_data", False))
            }
        except Exception as e:
            logger.warning(f"Gemini LLM contextual reasoning fallback triggered: {e}")
            return None

# Singleton instance
context_engine = ContextIntelligenceEngine()
