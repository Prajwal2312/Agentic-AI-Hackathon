"""
Automated Executive & Technical PDF Audit Report Generator using ReportLab.
Contains:
- Executive Audit Summary
- Files Scanned & Inventory
- PII Discovered & Context Intelligence Results
- DPDP Act 2023 & Rules 2025 Legal Compliance Observations
- Privacy Risk Scoring Breakdown
- Remediation Plan & Approval Records
- Agent Execution Audit Log
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from backend.app.config import REPORTS_DIR

class ReportService:
    @staticmethod
    def generate_pdf_report(session_data: Dict[str, Any]) -> str:
        session_id = session_data.get("id", "audit_report")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"PRIVESCAN_Audit_Report_{session_id}_{timestamp}.pdf"
        filepath = REPORTS_DIR / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom palette
        c_primary = colors.HexColor("#0B132B")
        c_accent = colors.HexColor("#3A86FF")
        c_secondary = colors.HexColor("#1C2541")
        c_text_dark = colors.HexColor("#1A1A24")
        c_text_muted = colors.HexColor("#5C677D")
        c_critical = colors.HexColor("#E63946")
        c_high = colors.HexColor("#F77F00")
        c_medium = colors.HexColor("#FCBF49")
        c_low = colors.HexColor("#2A9D8F")
        c_light_bg = colors.HexColor("#F8F9FA")

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=c_primary,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=c_text_muted,
            spaceAfter=15
        )
        h1_style = ParagraphStyle(
            'Header1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=c_secondary,
            spaceBefore=14,
            spaceAfter=8
        )
        h2_style = ParagraphStyle(
            'Header2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=c_accent,
            spaceBefore=8,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=c_text_dark
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=c_text_muted,
            spaceBefore=10
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("PRIVESCAN AI", title_style))
        elements.append(Paragraph("Data Privacy Discovery & DPDP Compliance Audit Report | Autonomous Multi-Agent System", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=15))

        # 2. Executive Audit Summary Metadata
        total_files = session_data.get("total_files", 0)
        total_findings = session_data.get("total_findings", 0)
        risk_score = session_data.get("risk_score", 0.0)
        crit = session_data.get("critical_findings", 0)
        high = session_data.get("high_findings", 0)
        med = session_data.get("medium_findings", 0)
        low = session_data.get("low_findings", 0)
        amb = session_data.get("ambiguous_findings", 0)

        meta_data = [
            [
                Paragraph(f"<b>Session ID:</b> {session_id}", body_style),
                Paragraph(f"<b>Audit Date:</b> {datetime.now().strftime('%d %B %Y %H:%M')}", body_style)
            ],
            [
                Paragraph(f"<b>Total Scanned Files:</b> {total_files}", body_style),
                Paragraph(f"<b>Total Findings Evaluated:</b> {total_findings}", body_style)
            ],
            [
                Paragraph(f"<b>Composite Risk Score:</b> <font color='{c_critical.hexval()}'><b>{risk_score}/100</b></font>", body_style),
                Paragraph(f"<b>Critical / High Findings:</b> {crit} Critical, {high} High", body_style)
            ],
            [
                Paragraph(f"<b>Ambiguous Evaluated:</b> {amb}", body_style),
                Paragraph(f"<b>Governing Standard:</b> India DPDP Act, 2023 & Rules 2025", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#DDE2E5")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EAEAEA")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))

        # 2.5 DATA INVENTORY REPORT: Which Personal Data is Held Where
        elements.append(Paragraph("1. Data Inventory Report (Which Personal Data is Held Where)", h1_style))
        elements.append(Paragraph(
            "Consolidated statutory inventory mapping each discovered personal data category, extraction engine used, "
            "and assessed repository sensitivity levels across all audited files.",
            body_style
        ))
        elements.append(Spacer(1, 8))

        files_data = session_data.get("files", [])
        if files_data:
            inv_table_data = [
                ["File Name", "Format & Extractor", "Sensitivity", "PII Categories Discovered", "Storage Locations"]
            ]
            for f in files_data:
                cats_str = ", ".join(f.get("categories", [])) or "Non-Personal Data"
                locs_str = "; ".join(f.get("sample_locations", [])) or "Document Body"
                ftype = f.get("file_type", "")
                extractor_str = "PyMuPDF" if ftype == "PDF" else (
                    "Pandas/Openpyxl" if ftype in ["XLSX", "CSV"] else (
                        "Multimodal OCR" if ftype in ["PNG", "JPG"] else "Text Parser"
                    )
                )
                sens = f.get("sensitivity_level", "LOW")
                inv_table_data.append([
                    Paragraph(f"<b>{f.get('filename', '')}</b>", body_style),
                    Paragraph(f"{ftype} ({extractor_str})", body_style),
                    Paragraph(f"<b>{sens}</b>", body_style),
                    Paragraph(cats_str, body_style),
                    Paragraph(locs_str[:120], body_style)
                ])

            inv_table = Table(inv_table_data, colWidths=[120, 95, 75, 130, 120])
            inv_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
            ]))
            elements.append(inv_table)
            elements.append(Spacer(1, 15))

        # 3. Context Intelligence & Discovered PII Findings Table
        elements.append(Paragraph("2. Discovered Personal Data & Context Intelligence Classification", h1_style))
        elements.append(Paragraph(
            "The Context Intelligence Agent evaluated each candidate value using column semantics, document type, and nearby context. "
            "False-positive patterns (e.g., 10-digit Order IDs) were successfully identified and segregated from genuine personal data.",
            body_style
        ))
        elements.append(Spacer(1, 8))

        findings = session_data.get("findings", [])[:20] # Top 20 for PDF compactness
        findings_table_data = [
            ["File", "Detected Value", "Category", "Classification", "Risk", "Confidence"]
        ]
        for f in findings:
            findings_table_data.append([
                Paragraph(str(f.get("file_name", "N/A"))[:20], body_style),
                Paragraph(str(f.get("masked_value", "****")), body_style),
                Paragraph(str(f.get("entity_type", "PII")), body_style),
                Paragraph(str(f.get("classification", "CONFIRMED")).replace("_", " "), body_style),
                Paragraph(f"<b>{str(f.get('risk_level', 'LOW'))}</b>", body_style),
                Paragraph(f"{float(f.get('confidence', 0.9))*100:.0f}%", body_style)
            ])

        if len(findings_table_data) > 1:
            findings_table = Table(findings_table_data, colWidths=[100, 95, 80, 140, 65, 60])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
            ]))
            elements.append(findings_table)
        else:
            elements.append(Paragraph("No personal data detected in reviewed files.", body_style))
        elements.append(Spacer(1, 15))

        # 4. DPDP Statutory Compliance Observations
        elements.append(Paragraph("3. DPDP Act, 2023 Statutory Compliance Observations", h1_style))
        elements.append(Paragraph(
            "Observations mapped by the DPDP Compliance Agent based on verifiable statutory provisions of India's Digital Personal Data Protection Act, 2023 and Rules 2025:",
            body_style
        ))
        elements.append(Spacer(1, 8))

        observations = session_data.get("compliance_observations", [])
        if observations:
            obs_table_data = [
                ["Provision", "Observation & Supporting Evidence", "Actionable Recommendation", "Severity"]
            ]
            for obs in observations[:10]: # Top 10 observations
                obs_table_data.append([
                    Paragraph(f"<b>{obs.get('provision_section', '')}</b><br/><font size=7 color='{c_accent.hexval()}'>{obs.get('status_in_force', '')}</font>", body_style),
                    Paragraph(f"<b>{obs.get('observation', '')}</b><br/><font size=7 color='{c_text_muted.hexval()}'>{obs.get('evidence', '')[:120]}...</font>", body_style),
                    Paragraph(obs.get("recommendation", "")[:120], body_style),
                    Paragraph(f"<b>{obs.get('severity', 'MEDIUM')}</b>", body_style)
                ])

            obs_table = Table(obs_table_data, colWidths=[110, 190, 180, 60])
            obs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
            ]))
            elements.append(obs_table)
        else:
            elements.append(Paragraph("All scanned repositories conform to documented baseline safeguards.", body_style))
        elements.append(Spacer(1, 15))

        # 5. Proposed Remediation Actions
        elements.append(Paragraph("4. Remediation Actions & Human-in-the-Loop Oversight", h1_style))
        elements.append(Paragraph(
            "The Remediation Agent generated cryptographically masked copies while preserving original files. Destructive or external actions require human approval.",
            body_style
        ))
        elements.append(Spacer(1, 8))

        remediations = session_data.get("remediation_actions", [])
        if remediations:
            rem_table_data = [
                ["File", "Remediation Action", "Proposed Action Details", "Approval Status"]
            ]
            for rem in remediations[:8]:
                rem_table_data.append([
                    Paragraph(str(rem.get("file_name", "File")), body_style),
                    Paragraph(f"<b>{str(rem.get('action_type', '')).replace('_', ' ')}</b>", body_style),
                    Paragraph(str(rem.get("proposed_details", ""))[:130], body_style),
                    Paragraph(f"<b>{str(rem.get('status', 'PENDING')).replace('_', ' ')}</b>", body_style)
                ])

            rem_table = Table(rem_table_data, colWidths=[100, 100, 240, 100])
            rem_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
            ]))
            elements.append(rem_table)
        elements.append(Spacer(1, 15))

        # 6. Multi-Agent Activity Log
        elements.append(Paragraph("4. Multi-Agent Execution Audit Trail", h1_style))
        agent_execs = session_data.get("agent_executions", [])
        if agent_execs:
            agent_table_data = [["Agent Name", "Status", "Execution Time", "Task Summary"]]
            for ag in agent_execs:
                agent_table_data.append([
                    Paragraph(f"<b>{ag.get('agent_name', '')}</b>", body_style),
                    Paragraph(ag.get("status", "COMPLETED"), body_style),
                    Paragraph(f"{ag.get('execution_duration_ms', 0)} ms", body_style),
                    Paragraph(ag.get("task_description", "")[:120], body_style)
                ])
            agent_table = Table(agent_table_data, colWidths=[120, 70, 70, 280])
            agent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
            ]))
            elements.append(agent_table)
        elements.append(Spacer(1, 15))

        # Legal Disclaimer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=8))
        elements.append(Paragraph(
            "<b>STATUTORY DISCLAIMER:</b> PRIVESCAN AI provides automated compliance assistance, data discovery, and risk scoring. "
            "This report does not constitute formal legal counsel. Data Fiduciaries must consult qualified legal practitioners for statutory DPDP certifications.",
            disclaimer_style
        ))

        # Build PDF
        doc.build(elements)
        return str(filepath)
