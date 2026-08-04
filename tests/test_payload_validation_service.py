from src.services.PayloadValidationService import PayloadValidationService


def build_valid_payload():
    return {
        "case_id": "MTG-2025-001",
        "name": "Sarah Johnson",
        "ssn": "123-45-6789",
        "email": "sarah.johnson@email.com",
        "phone": "555-234-5678",
        "address": "1234 Oak Street, San Francisco, CA 94102",
        "credit_score": 760,
        "credit_history": {
            "bankruptcies": 0,
            "foreclosures": 0,
            "late_payments_12mo": 0,
            "late_payments_24mo": 0,
            "collections": [],
            "inquiries_6mo": 2,
            "oldest_tradeline_years": 15,
            "total_tradelines": 12,
            "credit_notes": "Excellent payment history.",
        },
        "employment": {
            "employer": "Tech Solutions Inc",
            "position": "Senior Software Engineer",
            "years": 6.5,
            "monthly_income": 12500,
            "type": "W2",
            "employment_gap": "None",
            "gap_explanation": "N/A",
            "employment_history": [
                {
                    "employer": "Tech Solutions Inc",
                    "position": "Senior Software Engineer",
                    "years": 6.5,
                    "income": 150000,
                }
            ],
            "income_details": {
                "base_salary": 150000,
                "bonus_2023": 18000,
                "bonus_2024": 22000,
                "bonus_stable": True,
                "employer_confirmation": "Bonus likely to continue.",
            },
        },
        "debts": {
            "car_loan": 1200,
            "student_loan": 800,
            "credit_cards": 1800,
            "total_monthly_debt": 3800,
        },
        "assets": {
            "checking": 85000,
            "savings": 100000,
            "liquid_assets_total": 185000,
            "401k": 250000,
            "recent_deposits": [
                {
                    "date": "2024-12-15",
                    "amount": 22000,
                    "description": "Annual bonus",
                }
            ],
            "deposit_explanations": "December bonus documented.",
            "reserves_months": 18,
        },
        "loan": {
            "amount": 400000,
            "down_payment": 100000,
            "closing_costs": 12000,
            "estimated_payment": 3200,
            "property_type": "Single Family",
            "use": "Primary Residence",
            "monthly_piti": 3200,
        },
        "property": {
            "purchase_price": 500000,
            "appraised_value": 515000,
            "condition": "C3 - Average",
            "type": "Single Family Home",
            "required_repairs": 0,
            "repair_details": "No repairs required",
        },
        "dti_ratio": 0.304,
        "expected_decision": "APPROVED",
    }


def test_valid_payload_passes_validation():
    service = PayloadValidationService()
    payload = build_valid_payload()

    is_valid, errors = service.validate_payload(payload)

    assert is_valid is True
    assert errors == []


def test_missing_required_field_fails_validation():
    service = PayloadValidationService()
    payload = build_valid_payload()
    payload.pop("employment")

    is_valid, errors = service.validate_payload(payload)

    assert is_valid is False
    assert any("employment" in error for error in errors)
