from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class CreditHistory(BaseModel):
    bankruptcies: int = Field(ge=0)
    foreclosures: int = Field(ge=0)
    late_payments_12mo: int = Field(ge=0)
    late_payments_24mo: int = Field(ge=0)
    collections: list[Any]
    inquiries_6mo: int = Field(ge=0)
    oldest_tradeline_years: int = Field(ge=0)
    total_tradelines: int = Field(ge=0)
    credit_notes: str = Field(min_length=1)


class EmploymentHistoryEntry(BaseModel):
    employer: str = Field(min_length=1)
    position: str = Field(min_length=1)
    years: float = Field(ge=0)
    income: float = Field(ge=0)


class IncomeDetails(BaseModel):
    base_salary: float = Field(ge=0)
    bonus_2023: float = Field(ge=0)
    bonus_2024: float = Field(ge=0)
    bonus_stable: bool
    employer_confirmation: str = Field(min_length=1)


class Employment(BaseModel):
    employer: str = Field(min_length=1)
    position: str = Field(min_length=1)
    years: float = Field(ge=0)
    monthly_income: float = Field(ge=0)
    type: str = Field(min_length=1)
    employment_gap: str = Field(min_length=1)
    gap_explanation: str = Field(min_length=1)
    employment_history: list[EmploymentHistoryEntry]
    income_details: IncomeDetails


class Debts(BaseModel):
    car_loan: float = Field(ge=0)
    student_loan: float = Field(ge=0)
    credit_cards: float = Field(ge=0)
    total_monthly_debt: float = Field(ge=0)


class AssetDeposit(BaseModel):
    date: str = Field(min_length=1)
    amount: float = Field(ge=0)
    description: str = Field(min_length=1)


class Assets(BaseModel):
    checking: float = Field(ge=0)
    savings: float = Field(ge=0)
    liquid_assets_total: float = Field(ge=0)
    model_config = ConfigDict(populate_by_name=True)
    amt_401k: float = Field(alias="401k", ge=0)
    recent_deposits: list[AssetDeposit]
    deposit_explanations: str = Field(min_length=1)
    reserves_months: int = Field(ge=0)


class Loan(BaseModel):
    amount: float = Field(gt=0)
    down_payment: float = Field(ge=0)
    closing_costs: float = Field(ge=0)
    estimated_payment: float = Field(ge=0)
    property_type: str = Field(min_length=1)
    use: str = Field(min_length=1)
    monthly_piti: float = Field(ge=0)


class Property(BaseModel):
    purchase_price: float = Field(gt=0)
    appraised_value: float = Field(gt=0)
    condition: str = Field(min_length=1)
    type: str = Field(min_length=1)
    required_repairs: int = Field(ge=0)
    repair_details: str = Field(min_length=1)


class MortgagePayload(BaseModel):
    case_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    ssn: str
    email: str
    phone: str
    address: str = Field(min_length=1)
    credit_score: int = Field(ge=300, le=850)
    credit_history: CreditHistory
    employment: Employment
    debts: Debts
    assets: Assets
    loan: Loan
    property: Property
    dti_ratio: float = Field(ge=0, le=1)
    expected_decision: str = Field(min_length=1)

    model_config = ConfigDict(extra='forbid')

    @field_validator('ssn')
    @classmethod
    def validate_ssn(cls, value: str) -> str:
        if value and not __import__('re').fullmatch(r'\d{3}-\d{2}-\d{4}', value):
            raise ValueError('SSN must follow the format 123-45-6789')
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value and not __import__('re').fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', value):
            raise ValueError('Email must be a valid email address')
        return value

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if value and not __import__('re').fullmatch(r'\d{3}-\d{3}-\d{4}', value):
            raise ValueError('Phone must follow the format 555-234-5678')
        return value
