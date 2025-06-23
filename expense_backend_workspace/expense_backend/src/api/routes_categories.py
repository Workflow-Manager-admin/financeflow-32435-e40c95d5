"""
Router for expense categories (add, list, delete, edit).
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sqlite3
from . import database, auth, schemas

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=schemas.CategoryOut, summary="Add category")
def create_category(
    category: schemas.CategoryCreate,
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO categories (name, color, user_id) VALUES (?, ?, ?)",
        (category.name, category.color, user["id"])
    )
    db.commit()
    category_id = cursor.lastrowid
    return schemas.CategoryOut(id=category_id, name=category.name, color=category.color)


@router.get("/", response_model=List[schemas.CategoryOut], summary="List categories")
def get_categories(
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, name, color FROM categories WHERE user_id=?", (user["id"],)
    )
    cats = [schemas.CategoryOut(**dict(row)) for row in cursor.fetchall()]
    return cats


@router.delete("/{category_id}", status_code=204, summary="Delete category")
def delete_category(
    category_id: int,
    db: sqlite3.Connection = Depends(database.get_db),
    user=Depends(auth.get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM categories WHERE id=? AND user_id=?", (category_id, user["id"])
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    db.commit()
    return
