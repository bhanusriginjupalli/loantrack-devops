from decimal import Decimal

from pydantic import BaseModel, Field


class LoanCreate(BaseModel):
    borrower_name: str = Field(min_length=1)
    loan_amount: Decimal = Field(gt=0)
    property_city: str | None = None
    status: str = "PENDING"


class Loan(BaseModel):
    id: int
    borrower_name: str
    loan_amount: Decimal
    property_city: str | None
    status: str
    created_at: str