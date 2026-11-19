"""
Deterministic validation, regex patterns, and masking utilities for PII detection.
Includes specialized handling for Indian identifiers: Mobile, PAN, Aadhaar, Bank Accounts,
Emails, and Name candidate extraction.
"""

import re
from typing import Optional, Tuple, Dict, Any, List

# Regex Patterns
RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

# Indian Mobile: optionally starting with +91 or 0 or 91, followed by 6, 7, 8, 9 and 9 digits
RE_INDIAN_MOBILE_STRICT = re.compile(r'(?:(?:\+91|91|0)?[-\s]?)?([6-9]\d{9})\b')

# Generic 10-digit number (could be phone number OR order number OR tracking ID)
RE_GENERIC_10_DIGIT = re.compile(r'\b(\d{10})\b')

# Indian PAN: 5 uppercase letters, 4 digits, 1 uppercase letter (4th letter typically P, C, H, F, A, T, B, L, J, G)
RE_PAN = re.compile(r'\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b', re.IGNORECASE)

# Indian Aadhaar: 12 digits, often spaced or hyphenated (e.g., 1234 5678 9012 or 123456789012)
RE_AADHAAR = re.compile(r'\b(\d{4}[-\s]?\d{4}[-\s]?\d{4})\b')

# Bank Account Numbers: 9 to 18 digits (often surrounded by financial labels)
RE_BANK_ACCOUNT = re.compile(r'\b(\d{9,18})\b')

# Indian IFSC: 4 letters, 0, 6 alphanumeric (e.g., HDFC0001234)
RE_IFSC = re.compile(r'\b([A-Z]{4}0[A-Z0-9]{6})\b', re.IGNORECASE)

# Name detection heuristic: 2 to 4 capitalized words (excluding known non-name keywords)
RE_PERSON_NAME = re.compile(r'\b([A-Z][a-z]{2,20}(?:\s+[A-Z][a-z]{2,20}){1,3})\b')

NON_NAME_WORDS_SET = {
    # Address and Location words
    "road", "street", "lane", "cross", "main", "layout", "stage", "phase",
    "nagar", "colony", "enclave", "block", "floor", "building", "apartment",
    "district", "taluk", "village", "city", "town", "state", "pin", "postal",
    "north", "south", "east", "west", "central", "delhi", "mumbai", "bangalore",
    "bengaluru", "hyderabad", "chennai", "kolkata", "pune", "karnataka", "india",
    "united", "states", "america",
    
    # Resume / Academic / Professional terms
    "computer", "science", "information", "technology", "engineering", "bachelor",
    "master", "degree", "diploma", "school", "college", "university", "academy",
    "institute", "department", "semester", "year", "grade", "percentage", "cgpa",
    "board", "examination", "education", "qualifications", "curriculum", "vitae",
    "resume", "summary", "profile", "objective", "experience", "internship",
    "project", "projects", "skills", "languages", "programming", "database",
    "operating", "systems", "development", "developer", "management", "tools",
    "framework", "technologies", "software", "hardware", "system", "platform",
    "cloud", "network", "server", "native", "maps", "wires", "stack", "frontend",
    "backend", "fullstack", "front", "end", "back", "course", "certifications",
    "hackathon", "competition", "contest", "challenge", "winner", "runner",
    "topper", "captain", "sports", "basketball", "level", "round", "business",
    "safety", "tracking", "smart", "social", "artisan", "alley", "radar",
    "internal", "confidential", "declaration", "activities", "interests", "hobbies",
    "support", "policy", "gateway", "invoice", "report", "audit", "compliance",
    "details", "conditions", "limited", "private", "public", "terms", "service",
    "jumper", "wires", "react", "node", "angular", "python", "java", "script",
    "won", "first", "second", "third", "place", "prizes", "honor", "honors"
}

def extract_phone_digits(val: str) -> Optional[str]:
    """Normalizes and extracts 10-digit phone number if valid."""
    digits = re.sub(r'\D', '', str(val))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    return None

def is_person_name_candidate(val: str) -> bool:
    """Checks if a string resembles a person name (2-4 capitalized or title-case words)."""
    clean = str(val).strip()
    if len(clean) < 4 or len(clean) > 50:
        return False
    parts = clean.split()
    if 2 <= len(parts) <= 4:
        vowels = set("aeiouAEIOU")
        for p in parts:
            p_clean = p.rstrip(".").replace("-", "")
            if not p_clean.isalpha() or not p_clean[0].isupper():
                return False
            # Check if token is in common non-name words (address, tech, academic)
            if p_clean.lower() in NON_NAME_WORDS_SET:
                return False
            # Check presence of vowels in each name token
            if not any(char in vowels for char in p_clean):
                return False
        return True
    return False

def mask_value(val: str, entity_type: str) -> str:
    """Safely masks sensitive values for display and storage logs."""
    clean = str(val).strip()
    if not clean:
        return "****"

    if entity_type in ["EMAIL"]:
        if "@" in clean:
            parts = clean.split("@")
            user, domain = parts[0], parts[1]
            if len(user) <= 2:
                masked_user = user[0] + "*"
            else:
                masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
            return f"{masked_user}@{domain}"
        return clean[:2] + "****"

    if entity_type in ["PHONE", "MOBILE"]:
        # Show first 2 and last 2 or last 4
        digits = re.sub(r'\D', '', clean)
        if len(digits) >= 10:
            return f"+91 {digits[:2]}******{digits[-2:]}"
        return clean[:2] + "****" + clean[-2:] if len(clean) > 4 else "****"

    if entity_type == "PAN":
        clean = clean.upper()
        if len(clean) == 10:
            return f"{clean[:2]}***{clean[5:8]}*{clean[-1]}"
        return clean[:2] + "*****" + clean[-1]

    if entity_type == "AADHAAR":
        digits = re.sub(r'\D', '', clean)
        if len(digits) == 12:
            return f"**** **** {digits[-4:]}"
        return "**** **** " + clean[-4:] if len(clean) >= 4 else "****"

    if entity_type == "BANK_ACC":
        digits = re.sub(r'\D', '', clean)
        if len(digits) >= 6:
            return f"******{digits[-4:]}"
        return "******"

    if entity_type == "PERSON_NAME":
        parts = clean.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}*** {parts[-1][0]}***"
        return f"{clean[0]}***"

    # Default generic masking
    if len(clean) <= 4:
        return "****"
    return clean[:2] + "*" * (len(clean) - 4) + clean[-2:]

def validate_pan(pan_candidate: str) -> bool:
    """Verifies format and structure of Indian Permanent Account Number (PAN)."""
    clean = pan_candidate.strip().upper()
    if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', clean):
        return False
    # 4th character must be one of: P, C, H, F, A, T, B, L, J, G
    if clean[3] not in 'PCHFATBLJG':
        return False
    return True

def validate_aadhaar_verhoeff(aadhaar_str: str) -> bool:
    """Verhoeff algorithm checksum validation for 12-digit Indian Aadhaar."""
    digits = re.sub(r'\D', '', aadhaar_str)
    if len(digits) != 12:
        return False
    
    # Verhoeff multiplication and permutation tables
    d = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 6, 7, 8, 9, 0, 1, 2, 3, 4],
        [6, 7, 8, 9, 5, 1, 2, 3, 4, 0],
        [7, 8, 9, 5, 6, 2, 3, 4, 0, 1],
        [8, 9, 5, 6, 7, 3, 4, 0, 1, 2],
        [9, 5, 6, 7, 8, 4, 0, 1, 2, 3]
    ]
    p = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    
    c = 0
    inv_digits = digits[::-1]
    for i, char in enumerate(inv_digits):
        c = d[c][p[i % 8][int(char)]]
    return c == 0
