"""
Router for managing expenses and summary analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date
import sqlite3
from . import database, auth, schemas

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


def _category_info(db, category_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories WHERE id=?", (category_id,))
    row = cursor.fetchone()
    if row:
        return schemas.CategoryOut(id=row["id"], name=row["name"], color=row["color"])
    return None


@router.post("/", response_model=schemas.ExpenseOut, summary="Add an expense")
def add_expense(
    expense: schemas.ExpenseCreate,
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO expenses (user_id, category_id, amount, description, date)
           VALUES (?, ?, ?, ?, ?)""",
        (user["id"], expense.category_id, expense.amount, expense.description, expense.date)
    )
    db.commit()
    exp_id = cursor.lastrowid
    category = _category_info(db, expense.category_id)
    return schemas.ExpenseOut(
        id=exp_id,
        amount=expense.amount,
        description=expense.description,
        date=expense.date,
        category=category
    )


@router.get("/", response_model=List[schemas.ExpenseOut], summary="Get expenses")
def list_expenses(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    if start_date and end_date:
        cursor.execute(
            """SELECT e.id, e.amount, e.description, e.date, c.id as cat_id, c.name as cat_name,
                c.color as cat_color
               FROM expenses e JOIN categories c ON e.category_id=c.id
               WHERE e.user_id=? AND date BETWEEN ? AND ? ORDER BY date DESC""",
            (user["id"], start_date, end_date)
        )
    else:
        cursor.execute(
            """SELECT e.id, e.amount, e.description, e.date, c.id as cat_id, c.name as cat_name,
                c.color as cat_color
               FROM expenses e JOIN categories c ON e.category_id=c.id
               WHERE e.user_id=? ORDER BY date DESC""",
            (user["id"],)
        )
    results = []
    for row in cursor.fetchall():
        category = schemas.CategoryOut(
            id=row["cat_id"],
            name=row["cat_name"],
            color=row["cat_color"]
        )
        results.append(
            schemas.ExpenseOut(
                id=row["id"],
                amount=row["amount"],
                description=row["description"],
                date=row["date"],
                category=category
            )
        )
    return results


@router.put("/{expense_id}", response_model=schemas.ExpenseOut, summary="Edit expense")
def edit_expense(
    expense_id: int,
    expense: schemas.ExpenseCreate,
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    # Ensure expense exists and belongs to user
    cursor.execute("SELECT * FROM expenses WHERE id=? AND user_id=?", (expense_id, user["id"]))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Expense not found")
    cursor.execute(
        "UPDATE expenses SET category_id=?, amount=?, description=?, date=? WHERE id=?",
        (expense.category_id, expense.amount, expense.description, expense.date, expense_id)
    )
    db.commit()
    category = _category_info(db, expense.category_id)
    return schemas.ExpenseOut(
        id=expense_id,
        amount=expense.amount,
        description=expense.description,
        date=expense.date,
        category=category
    )


@router.delete("/{expense_id}", status_code=204, summary="Delete expense")
def delete_expense(
    expense_id: int,
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user["id"]))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.commit()
    return


@router.get("/summary/monthly", response_model=schemas.MonthlySummary, summary="Monthly summary")
def monthly_summary(
    year: int, month: int,
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    month_str = f"{year:04d}-{month:02d}"
    # Total amount for this month
    cursor.execute(
        """SELECT SUM(amount) as total FROM expenses
           WHERE user_id=? AND strftime('%Y-%m', date)=?""",
        (user["id"], month_str)
    )
    total = cursor.fetchone()["total"] or 0.0
    # By category
    cursor.execute(
        """SELECT c.name, c.color, SUM(e.amount) as total FROM expenses e
           JOIN categories c ON e.category_id=c.id
           WHERE e.user_id=? AND strftime('%Y-%m', e.date)=?
           GROUP BY e.category_id""",
        (user["id"], month_str)
    )
    by_category = []
    for row in cursor.fetchall():
        by_category.append({
            "name": row["name"],
            "color": row["color"],
            "total": row["total"]
        })
    return schemas.MonthlySummary(
        month=month_str, total_amount=total, by_category=by_category
    )
