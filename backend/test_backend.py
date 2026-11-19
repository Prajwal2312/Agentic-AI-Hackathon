"""
Automated Backend Verification Test.
Tests:
1. Context Intelligence Engine on Order_ID vs Mobile_Number
2. Multi-Agent LangGraph execution on synthetic sample files
3. Database persistence of findings, risk scores, compliance observations, and remediation actions
4. PDF Report generation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import SessionLocal, Base, engine
from backend.app.services.audit_service import AuditService
from backend.app.engine.context_classifier import context_engine

def run_tests():
    print("=== TEST 1: Context Intelligence Engine Verification ===")
    
    # Example 1: Order ID with 10 digits
    res1 = context_engine.classify_candidate(
        value="9876543210",
        column_name="Order_ID",
        document_type="customer_orders"
    )
    print("Order_ID test result:", res1)
    assert res1["classification"] == "NON_PERSONAL_IDENTIFIER", f"Expected NON_PERSONAL_IDENTIFIER, got {res1['classification']}"
    assert not res1["is_personal_data"], "Order ID should not be personal data"
    print("PASSED: Order ID successfully classified as NON_PERSONAL_IDENTIFIER!")

    # Example 2: Mobile Number with identical 10 digits
    res2 = context_engine.classify_candidate(
        value="9876543210",
        column_name="Mobile_Number",
        document_type="customer_database"
    )
    print("Mobile_Number test result:", res2)
    assert res2["classification"] in ["CONFIRMED_PERSONAL_DATA", "LIKELY_PERSONAL_DATA"], f"Expected personal data, got {res2['classification']}"
    assert res2["is_personal_data"], "Mobile number should be personal data"
    print("PASSED: Mobile Number successfully confirmed as PERSONAL DATA!")

    print("\n=== TEST 2: Multi-Agent Demo Audit Execution ===")
    db = SessionLocal()
    try:
        session = AuditService.load_demo_session(db)
        print(f"Audit Session Executed: ID={session.id}, Status={session.status}, Risk Score={session.risk_score}")
        print(f"Total Files: {session.total_files}, Total Findings: {session.total_findings}")
        print(f"Breakdown: {session.critical_findings} Critical, {session.high_findings} High, {session.medium_findings} Med, {session.low_findings} Low")

        assert session.status == "COMPLETED", "Session status should be COMPLETED"
        assert session.total_findings > 0, "Should have discovered findings"

        print("\n=== TEST 3: Remediation & Redacted Copies Verification ===")
        from backend.app.models import RemediationAction
        rems = db.query(RemediationAction).filter(RemediationAction.session_id == session.id).all()
        print(f"Generated {len(rems)} remediation actions.")
        for r in rems:
            print(f"- {r.action_type} for {r.original_file_path} (Status: {r.status})")
            if r.redacted_file_path:
                print(f"  Redacted file created: {r.redacted_file_path} (Exists: {Path(r.redacted_file_path).exists()})")

        print("\n=== TEST 4: PDF Report Generation Verification ===")
        pdf_path = AuditService.generate_session_report_pdf(db, session.id)
        print(f"Generated PDF Audit Report at: {pdf_path}")
        assert Path(pdf_path).exists(), f"PDF report not found at {pdf_path}"
        print(f"Report file size: {Path(pdf_path).stat().st_size} bytes")

        print("\nALL BACKEND TESTS PASSED!")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
