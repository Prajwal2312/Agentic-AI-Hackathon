"""
Generates synthetic benchmark test files for PRIVESCAN AI:
1. customer_database.xlsx (Tabular customer database with Order IDs vs Mobile Numbers)
2. employee_records.pdf (HR master document with PAN, Aadhaar, Bank Details, and Phone)
3. old_customer_export.csv (Legacy export file with misleading Order IDs matching phone formats)
"""

from pathlib import Path
import pandas as pd
import fitz # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SAMPLE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def generate_customer_database_excel():
    excel_path = SAMPLE_DIR / "customer_database.xlsx"
    
    # Intentionally placing 10-digit Order IDs next to 10-digit Phone Numbers!
    # E.g. Order_ID: 9876543210 vs Mobile_Number: 9876543210
    data = [
        {
            "Customer_ID": "CUST-1001",
            "Customer_Name": "Aarav Sharma",
            "Order_ID": "9876543210",          # 10-digit order ID - MISLEADING FALSE POSITIVE!
            "Mobile_Number": "9876543210",     # 10-digit genuine mobile phone
            "Email": "aarav.sharma@example.com",
            "City": "Mumbai",
            "PAN_Number": "AAAPS1234K",        # Individual PAN
            "Account_Number": "9123456789012"  # 13-digit Bank Account
        },
        {
            "Customer_ID": "CUST-1002",
            "Customer_Name": "Priya Patel",
            "Order_ID": "9123456780",          # 10-digit order ID
            "Mobile_Number": "9123456789",     # 10-digit genuine mobile phone
            "Email": "priya.patel@corporate.in",
            "City": "Ahmedabad",
            "PAN_Number": "BCCPP5678L",        # Individual PAN
            "Account_Number": "987654321098"   # 12-digit Bank Account
        },
        {
            "Customer_ID": "CUST-1003",
            "Customer_Name": "Vikram Malhotra",
            "Order_ID": "8765432109",          # 10-digit order ID
            "Mobile_Number": "8765432190",     # 10-digit mobile
            "Email": "vikram.m@domain.co.in",
            "City": "Bengaluru",
            "PAN_Number": "CPMPM9012M",
            "Account_Number": "50100234567891"
        },
        {
            "Customer_ID": "CUST-1004",
            "Customer_Name": "Ananya Sen",
            "Order_ID": "7654321098",          # 10-digit order ID
            "Mobile_Number": "7654321089",     # 10-digit mobile
            "Email": "ananya.sen@webmail.org",
            "City": "Kolkata",
            "PAN_Number": "DPPSA3456N",
            "Account_Number": "60200456781234"
        },
        {
            "Customer_ID": "CUST-1005",
            "Customer_Name": "Rohan Deshmukh",
            "Order_ID": "9988776655",          # 10-digit order ID
            "Mobile_Number": "9988776644",     # 10-digit mobile
            "Email": "rohan.deshmukh@fintech.io",
            "City": "Pune",
            "PAN_Number": "EPPRD7890P",
            "Account_Number": "30400129876543"
        }
    ]
    df = pd.DataFrame(data)
    df.to_excel(excel_path, sheet_name="Customer_Master", index=False)
    print(f"Created: {excel_path}")

def generate_old_customer_export_csv():
    csv_path = SAMPLE_DIR / "old_customer_export.csv"
    
    # Legacy CSV dump with order transactions and mixed fields
    data = [
        {
            "Transaction_ID": "TXN9876543210",
            "Order_ID": "9876543210",          # 10-digit Order ID
            "Client_Name": "Sunita Reddy",
            "Contact_Phone": "9849012345",
            "Contact_Email": "sunita.reddy@techcorp.com",
            "Aadhaar_Number": "9876 5432 1098", # 12-digit Aadhaar
            "Billing_City": "Hyderabad",
            "Payment_Status": "COMPLETED",
            "Invoice_Amount_INR": "45200.00"
        },
        {
            "Transaction_ID": "TXN9123456780",
            "Order_ID": "9123456780",          # 10-digit Order ID
            "Client_Name": "Rajesh Nair",
            "Contact_Phone": "9447098765",
            "Contact_Email": "rajesh.nair@logisticshub.net",
            "Aadhaar_Number": "8765 4321 0987", # 12-digit Aadhaar
            "Billing_City": "Kochi",
            "Payment_Status": "SETTLED",
            "Invoice_Amount_INR": "18900.50"
        },
        {
            "Transaction_ID": "TXN8765432109",
            "Order_ID": "8765432109",          # 10-digit Order ID
            "Client_Name": "Deepak Verma",
            "Contact_Phone": "9811234567",
            "Contact_Email": "deepak.verma@consultancy.in",
            "Aadhaar_Number": "7654 3210 9876", # 12-digit Aadhaar
            "Billing_City": "New Delhi",
            "Payment_Status": "PENDING",
            "Invoice_Amount_INR": "95000.00"
        },
        {
            "Transaction_ID": "TXN7654321098",
            "Order_ID": "7654321098",          # 10-digit Order ID
            "Client_Name": "Meera Iyer",
            "Contact_Phone": "9840198765",
            "Contact_Email": "meera.iyer@creativestudios.co",
            "Aadhaar_Number": "6543 2109 8765", # 12-digit Aadhaar
            "Billing_City": "Chennai",
            "Payment_Status": "COMPLETED",
            "Invoice_Amount_INR": "32400.00"
        }
    ]
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"Created: {csv_path}")

def generate_employee_records_pdf():
    pdf_path = SAMPLE_DIR / "employee_records.pdf"
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'EmpTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor("#0B132B"),
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'EmpBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222")
    )

    elements = [
        Paragraph("CONFIDENTIAL: Employee Personnel Records & KYC Master", title_style),
        Paragraph("Internal HR Compliance Document | Retain under Statutory Employment Mandate", body_style),
        Spacer(1, 15)
    ]

    emp_data = [
        ["Emp ID", "Employee Name", "Designation", "Official Email", "Mobile Number", "PAN", "Bank Account Number"],
        ["EMP-001", "Kavita Krishnan", "Lead Architect", "kavita.k@company.internal", "9870123456", "ABCDE1234F", "102030405060"],
        ["EMP-002", "Siddharth Joshi", "Security Engineer", "siddharth.j@company.internal", "9820987654", "BCDEF5678G", "203040506070"],
        ["EMP-003", "Neha Singhania", "Product Manager", "neha.s@company.internal", "9830567890", "CDEFG9012H", "304050607080"],
        ["EMP-004", "Manish Kapoor", "DevOps Specialist", "manish.k@company.internal", "9890123789", "DEFGH3456J", "405060708090"]
    ]

    emp_table = Table(emp_data, colWidths=[55, 95, 85, 120, 75, 65, 80])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1C2541")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")])
    ]))

    elements.append(emp_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "<b>Notice to HR Staff:</b> Access to personnel records is restricted pursuant to Section 8(5) of the DPDP Act 2023. "
        "Any unencrypted dissemination to public cloud folders constitutes an internal security violation.",
        body_style
    ))

    doc.build(elements)
    print(f"Created: {pdf_path}")

def generate_scanned_image_sample():
    """Generates a synthetic scanned KYC application image (PNG) with text and PNG metadata."""
    from PIL import Image, ImageDraw, PngImagePlugin
    
    img_path = SAMPLE_DIR / "scanned_kyc_application.png"
    sidecar_path = SAMPLE_DIR / "scanned_kyc_application.ocr.txt"
    
    w, h = 800, 600
    img = Image.new("RGB", (w, h), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)
    
    # Border & Header
    draw.rectangle([(15, 15), (w - 15, h - 15)], outline=(180, 190, 205), width=2)
    draw.rectangle([(20, 20), (w - 20, 75)], fill=(30, 41, 59))
    draw.text((35, 35), "STATE PRIVACY CO-OPERATIVE: KYC & IDENTITY AUDIT RECORD", fill=(255, 255, 255))
    
    # Key-value lines
    lines = [
        "Application Form ID: 9944112233",             # 10-digit Non-personal identifier
        "Applicant Full Name: Rajesh Kumar Verma",     # Person name
        "Primary Contact Mobile: 9845123456",           # Genuine 10-digit mobile
        "Aadhaar Number: 3675 9834 5012",              # Aadhaar PII
        "PAN Card: ABCPV1234E",                        # Valid PAN
        "Email Address: rajesh.verma@domain.in",       # Email
        "Bank Account Number: 50100456789123",         # Bank account
        "KYC Document Status: VERIFIED",
        "Submission Date: 2026-04-12"
    ]
    
    ocr_text_content = "\n".join(lines)
    
    # Draw lines onto image
    y_start = 110
    for idx, text in enumerate(lines):
        y = y_start + (idx * 46)
        # Draw background stripe
        if idx % 2 == 0:
            draw.rectangle([(25, y - 5), (w - 25, y + 30)], fill=(240, 243, 248))
        draw.text((40, y), text, fill=(33, 37, 41))
    
    # Save with PNG tEXt metadata chunk
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("ocr_text", ocr_text_content)
    png_info.add_text("Description", "Scanned KYC Onboarding Form with Multimodal OCR")
    
    img.save(img_path, pnginfo=png_info)
    
    # Also write sidecar text file for zero-dependency test robustness
    with open(sidecar_path, "w", encoding="utf-8") as f:
        f.write(ocr_text_content)
        
    print(f"Created: {img_path}")

if __name__ == "__main__":
    generate_customer_database_excel()
    generate_old_customer_export_csv()
    generate_employee_records_pdf()
    generate_scanned_image_sample()
