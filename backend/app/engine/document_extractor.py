"""
Multi-format Document Extraction Engine.
Extracts structured text, tabular records, column headers, and metadata from:
- PDF (PyMuPDF / fitz)
- DOCX (python-docx)
- XLSX (openpyxl / pandas)
- CSV (pandas / csv)
- TXT (standard library)
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

class DocumentRecord:
    def __init__(
        self,
        value: str,
        column_name: Optional[str] = None,
        row_idx: Optional[int] = None,
        col_idx: Optional[int] = None,
        page_number: Optional[int] = None,
        location_desc: Optional[str] = None,
        surrounding_text: Optional[str] = None,
        document_type: Optional[str] = None,
        entity_hint: Optional[str] = None
    ):
        self.value = str(value).strip()
        self.column_name = column_name or ""
        self.row_idx = row_idx
        self.col_idx = col_idx
        self.page_number = page_number
        self.location_desc = location_desc or ""
        self.surrounding_text = surrounding_text or ""
        self.document_type = document_type or ""
        self.entity_hint = entity_hint

class DocumentExtractor:
    @staticmethod
    def extract(file_path: str) -> List[DocumentRecord]:
        path = Path(file_path)
        ext = path.suffix.lower()
        doc_type = path.stem.lower()

        if ext == ".csv":
            return DocumentExtractor._extract_csv(path, doc_type)
        elif ext in [".xlsx", ".xls"]:
            return DocumentExtractor._extract_excel(path, doc_type)
        elif ext == ".pdf":
            return DocumentExtractor._extract_pdf(path, doc_type)
        elif ext == ".docx":
            return DocumentExtractor._extract_docx(path, doc_type)
        elif ext == ".txt":
            return DocumentExtractor._extract_txt(path, doc_type)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]:
            return DocumentExtractor._extract_image(path, doc_type)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _extract_csv(path: Path, doc_type: str) -> List[DocumentRecord]:
        records: List[DocumentRecord] = []
        try:
            df = pd.read_csv(path, dtype=str).fillna("")
            for row_idx, row in df.iterrows():
                for col_idx, col_name in enumerate(df.columns):
                    val = str(row[col_name]).strip()
                    if val and val != "nan":
                        # Capture surrounding fields in the same row as contextual evidence
                        context = " | ".join([f"{c}: {row[c]}" for c in df.columns if c != col_name and str(row[c]).strip()])
                        records.append(DocumentRecord(
                            value=val,
                            column_name=str(col_name),
                            row_idx=int(row_idx) + 1,
                            col_idx=col_idx + 1,
                            location_desc=f"Row {int(row_idx) + 1}, Column '{col_name}'",
                            surrounding_text=context[:300],
                            document_type=doc_type
                        ))
        except Exception as e:
            # Fallback to standard line parser
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            if lines:
                headers = [h.strip().replace('"', '') for h in lines[0].split(",")]
                for r_idx, line in enumerate(lines[1:], start=2):
                    parts = [p.strip().replace('"', '') for p in line.split(",")]
                    for c_idx, val in enumerate(parts):
                        col_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx+1}"
                        if val:
                            records.append(DocumentRecord(
                                value=val,
                                column_name=col_name,
                                row_idx=r_idx,
                                col_idx=c_idx + 1,
                                location_desc=f"Row {r_idx}, Column '{col_name}'",
                                surrounding_text=line.strip()[:300],
                                document_type=doc_type
                            ))
        return records

    @staticmethod
    def _extract_excel(path: Path, doc_type: str) -> List[DocumentRecord]:
        records: List[DocumentRecord] = []
        excel_file = pd.ExcelFile(path)
        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name, dtype=str).fillna("")
            for row_idx, row in df.iterrows():
                for col_idx, col_name in enumerate(df.columns):
                    val = str(row[col_name]).strip()
                    if val and val != "nan":
                        context = " | ".join([f"{c}: {row[c]}" for c in df.columns if c != col_name and str(row[c]).strip()])
                        records.append(DocumentRecord(
                            value=val,
                            column_name=str(col_name),
                            row_idx=int(row_idx) + 1,
                            col_idx=col_idx + 1,
                            location_desc=f"Sheet '{sheet_name}', Row {int(row_idx) + 1}, Col '{col_name}'",
                            surrounding_text=context[:300],
                            document_type=f"{doc_type}_{sheet_name}".lower()
                        ))
        return records

    @staticmethod
    def _extract_pdf(path: Path, doc_type: str) -> List[DocumentRecord]:
        records: List[DocumentRecord] = []
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            text = page.get_text("text")
            lines = text.split("\n")
            
            for line_idx, line in enumerate(lines):
                line_str = line.strip()
                if not line_str:
                    continue
                
                # Extract structured PII entities directly from full line (Email, Phone, Name, PAN, Aadhaar)
                line_entities = DocumentExtractor._extract_line_entities(line_str, page_num, line_idx + 1, doc_type)
                records.extend(line_entities)

                # Check for "Label: Value" pattern (e.g. "Mobile: 9876543210", "Order ID: 9876543210", "PAN: ABCDE1234F")
                if ":" in line_str:
                    parts = line_str.split(":", 1)
                    label = parts[0].strip()
                    val = parts[1].strip()
                    if val and not any(e.value == val for e in line_entities):
                        records.append(DocumentRecord(
                            value=val,
                            column_name=label,
                            page_number=page_num,
                            row_idx=line_idx + 1,
                            location_desc=f"Page {page_num}, Line: '{label}'",
                            surrounding_text=line_str,
                            document_type=doc_type
                        ))
                elif not line_entities:
                    # Provide tokenized line elements fallback
                    words = line_str.split()
                    for word in words:
                        clean_w = word.strip(",;.()[]{}")
                        if len(clean_w) >= 3:
                            records.append(DocumentRecord(
                                value=clean_w,
                                column_name="",
                                page_number=page_num,
                                row_idx=line_idx + 1,
                                location_desc=f"Page {page_num}, Line {line_idx + 1}",
                                surrounding_text=line_str[:250],
                                document_type=doc_type
                            ))
        doc.close()
        return records

    @staticmethod
    def _extract_docx(path: Path, doc_type: str) -> List[DocumentRecord]:
        records: List[DocumentRecord] = []
        import docx
        doc = docx.Document(str(path))
        
        # 1. Paragraphs
        for p_idx, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if not text:
                continue

            line_entities = DocumentExtractor._extract_line_entities(text, None, p_idx + 1, doc_type)
            records.extend(line_entities)

            if ":" in text:
                parts = text.split(":", 1)
                label = parts[0].strip()
                val = parts[1].strip()
                if val and not any(e.value == val for e in line_entities):
                    records.append(DocumentRecord(
                        value=val,
                        column_name=label,
                        row_idx=p_idx + 1,
                        location_desc=f"Paragraph {p_idx + 1}, Label '{label}'",
                        surrounding_text=text[:300],
                        document_type=doc_type
                    ))
            elif not line_entities:
                for word in text.split():
                    clean_w = word.strip(",;.()[]{}")
                    if len(clean_w) >= 3:
                        records.append(DocumentRecord(
                            value=clean_w,
                            column_name="",
                            row_idx=p_idx + 1,
                            location_desc=f"Paragraph {p_idx + 1}",
                            surrounding_text=text[:300],
                            document_type=doc_type
                        ))

        # 2. Tables
        for t_idx, table in enumerate(doc.tables):
            headers = []
            for r_idx, row in enumerate(table.rows):
                cells = [c.text.strip() for c in row.cells]
                if r_idx == 0:
                    headers = cells
                else:
                    for c_idx, val in enumerate(cells):
                        col_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx+1}"
                        if val:
                            row_context = " | ".join([f"{headers[i] if i < len(headers) else f'Col_{i+1}'}: {c}" for i, c in enumerate(cells) if i != c_idx and c])
                            records.append(DocumentRecord(
                                value=val,
                                column_name=col_name,
                                row_idx=r_idx + 1,
                                col_idx=c_idx + 1,
                                location_desc=f"Table {t_idx + 1}, Row {r_idx + 1}, Col '{col_name}'",
                                surrounding_text=row_context[:300],
                                document_type=doc_type
                            ))
        return records

    @staticmethod
    def _extract_txt(path: Path, doc_type: str) -> List[DocumentRecord]:
        records: List[DocumentRecord] = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for l_idx, line in enumerate(f, start=1):
                line_str = line.strip()
                if not line_str:
                    continue

                line_entities = DocumentExtractor._extract_line_entities(line_str, None, l_idx, doc_type)
                records.extend(line_entities)

                if ":" in line_str:
                    parts = line_str.split(":", 1)
                    label = parts[0].strip()
                    val = parts[1].strip()
                    if val and not any(e.value == val for e in line_entities):
                        records.append(DocumentRecord(
                            value=val,
                            column_name=label,
                            row_idx=l_idx,
                            location_desc=f"Line {l_idx}, Label '{label}'",
                            surrounding_text=line_str[:300],
                            document_type=doc_type
                        ))
                elif not line_entities:
                    for word in line_str.split():
                        clean_w = word.strip(",;.()[]{}")
                        if len(clean_w) >= 3:
                            records.append(DocumentRecord(
                                value=clean_w,
                                column_name="",
                                row_idx=l_idx,
                                location_desc=f"Line {l_idx}",
                                surrounding_text=line_str[:300],
                                document_type=doc_type
                            ))
        return records

    @staticmethod
    def _extract_line_entities(line_str: str, page_num: Optional[int], row_idx: int, doc_type: str) -> List[DocumentRecord]:
        """Extracts structured personal data entities directly from natural language lines."""
        from backend.app.engine.pii_rules import (
            RE_EMAIL, RE_PAN, RE_AADHAAR, RE_PERSON_NAME,
            extract_phone_digits, is_person_name_candidate
        )
        import re
        
        entities: List[DocumentRecord] = []
        loc = f"Page {page_num}, Line {row_idx}" if page_num else f"Line {row_idx}"
        
        # 1. Emails
        for m in RE_EMAIL.finditer(line_str):
            entities.append(DocumentRecord(
                value=m.group().strip(),
                column_name="Email Address",
                page_number=page_num,
                row_idx=row_idx,
                location_desc=f"{loc} (Email)",
                surrounding_text=line_str[:300],
                document_type=doc_type,
                entity_hint="EMAIL"
            ))

        # 2. Phone Numbers (Indian and international, e.g. +91 98765 43210, 9876543210, 98765-43210, 09876543210)
        phone_matches = re.finditer(r'(?:(?:\+91|91|0)?[-\s.]?)?(?:[6-9]\d{2}[-\s.]?\d{3}[-\s.]?\d{4})\b', line_str)
        for m in phone_matches:
            match_str = m.group().strip()
            if extract_phone_digits(match_str):
                entities.append(DocumentRecord(
                    value=match_str,
                    column_name="Phone Number",
                    page_number=page_num,
                    row_idx=row_idx,
                    location_desc=f"{loc} (Phone)",
                    surrounding_text=line_str[:300],
                    document_type=doc_type,
                    entity_hint="PHONE"
                ))

        # 3. PAN Cards
        for m in RE_PAN.finditer(line_str):
            entities.append(DocumentRecord(
                value=m.group().strip(),
                column_name="PAN Card",
                page_number=page_num,
                row_idx=row_idx,
                location_desc=f"{loc} (PAN)",
                surrounding_text=line_str[:300],
                document_type=doc_type,
                entity_hint="PAN"
            ))

        # 4. Aadhaar Numbers
        for m in RE_AADHAAR.finditer(line_str):
            entities.append(DocumentRecord(
                value=m.group().strip(),
                column_name="Aadhaar Number",
                page_number=page_num,
                row_idx=row_idx,
                location_desc=f"{loc} (Aadhaar)",
                surrounding_text=line_str[:300],
                document_type=doc_type,
                entity_hint="AADHAAR"
            ))

        # 5. Person Names (2-4 capitalized words)
        for m in RE_PERSON_NAME.finditer(line_str):
            candidate_name = m.group().strip()
            if is_person_name_candidate(candidate_name):
                entities.append(DocumentRecord(
                    value=candidate_name,
                    column_name="Person Name",
                    page_number=page_num,
                    row_idx=row_idx,
                    location_desc=f"{loc} (Name)",
                    surrounding_text=line_str[:300],
                    document_type=doc_type,
                    entity_hint="PERSON_NAME"
                ))

        return entities

    @staticmethod
    def _extract_image(path: Path, doc_type: str) -> List[DocumentRecord]:
        records: List[DocumentRecord] = []
        raw_text = ""
        
        # 1. Attempt Multimodal Gemini Vision OCR if GEMINI_API_KEY is configured
        from backend.app.config import settings
        if settings.GEMINI_API_KEY:
            try:
                raw_text = DocumentExtractor._ocr_with_gemini(path)
            except Exception as e:
                print(f"[OCR] Gemini Vision note: {e}")
                
        # 2. Check for embedded PNG text chunk metadata (PNG standard tEXt)
        if not raw_text:
            try:
                from PIL import Image
                with Image.open(path) as img:
                    if hasattr(img, "text") and img.text:
                        raw_text = img.text.get("ocr_text", "") or img.text.get("Description", "")
            except Exception:
                pass
                
        # 3. Check for companion sidecar text (.ocr.txt or same stem .txt)
        if not raw_text:
            sidecar = path.with_suffix(".ocr.txt")
            if sidecar.exists():
                raw_text = sidecar.read_text(encoding="utf-8", errors="ignore")
            else:
                sidecar_txt = path.with_suffix(".txt")
                if sidecar_txt.exists():
                    raw_text = sidecar_txt.read_text(encoding="utf-8", errors="ignore")
                    
        # 4. Parse extracted OCR text into structured DocumentRecords
        if raw_text:
            lines = raw_text.split("\n")
            for line_idx, line in enumerate(lines, start=1):
                line_str = line.strip()
                if not line_str:
                    continue

                line_entities = DocumentExtractor._extract_line_entities(line_str, None, line_idx, doc_type)
                records.extend(line_entities)

                if ":" in line_str:
                    parts = line_str.split(":", 1)
                    label = parts[0].strip()
                    val = parts[1].strip()
                    if val and not any(e.value == val for e in line_entities):
                        records.append(DocumentRecord(
                            value=val,
                            column_name=label,
                            row_idx=line_idx,
                            location_desc=f"Scanned Image OCR, Line {line_idx}: '{label}'",
                            surrounding_text=line_str[:300],
                            document_type=doc_type
                        ))
                elif not line_entities:
                    for word in line_str.split():
                        clean_w = word.strip(",;.()[]{}")
                        if len(clean_w) >= 3:
                            records.append(DocumentRecord(
                                value=clean_w,
                                column_name="",
                                row_idx=line_idx,
                                location_desc=f"Scanned Image OCR, Line {line_idx}",
                                surrounding_text=line_str[:300],
                                document_type=doc_type
                            ))
        return records

    @staticmethod
    def _ocr_with_gemini(path: Path) -> str:
        """Performs high-fidelity multimodal OCR using Google Gemini Vision."""
        from google import genai
        from google.genai import types
        from backend.app.config import settings
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        with open(path, "rb") as f:
            image_bytes = f.read()
            
        ext = path.suffix.lower().replace(".", "")
        mime = "image/png" if ext == "png" else f"image/{ext}"
        
        prompt = (
            "You are an OCR and document parser agent. "
            "Extract all readable text, key-value pairs (e.g., Name: ..., Mobile: ..., Aadhaar: ..., "
            "PAN: ..., Form_ID: ..., Order_ID: ...), and printed details from this document image. "
            "Format the output strictly as key: value pairs where applicable, or line-separated text."
        )
        
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=mime)
            ]
        )
        return response.text or ""
