from fastapi import APIRouter, HTTPException, Request, status

from .models import LoanCreate


router = APIRouter()


@router.get("/loans")
def get_loans(request: Request):
    pool = request.app.state.db_pool

    with pool.connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                borrower_name,
                loan_amount,
                property_city,
                status,
                created_at
            FROM loans
            ORDER BY id
            """
        ).fetchall()

    return [
        {
            "id": row[0],
            "borrower_name": row[1],
            "loan_amount": float(row[2]),
            "property_city": row[3],
            "status": row[4],
            "created_at": row[5].isoformat(),
        }
        for row in rows
    ]


@router.post("/loans", status_code=status.HTTP_201_CREATED)
def create_loan(loan: LoanCreate, request: Request):
    pool = request.app.state.db_pool

    with pool.connection() as connection:
        row = connection.execute(
            """
            INSERT INTO loans (
                borrower_name,
                loan_amount,
                property_city,
                status
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                id,
                borrower_name,
                loan_amount,
                property_city,
                status,
                created_at
            """,
            (
                loan.borrower_name,
                loan.loan_amount,
                loan.property_city,
                loan.status,
            ),
        ).fetchone()

        connection.commit()

    return {
        "id": row[0],
        "borrower_name": row[1],
        "loan_amount": float(row[2]),
        "property_city": row[3],
        "status": row[4],
        "created_at": row[5].isoformat(),
    }


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.get("/readyz")
def readyz(request: Request):
    pool = request.app.state.db_pool

    try:
        with pool.connection() as connection:
            connection.execute("SELECT 1")

        return {"status": "ready"}

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {exc}",
        )