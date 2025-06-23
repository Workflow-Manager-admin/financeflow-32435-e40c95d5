"""
Authentication and registration router.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from . import database, auth, schemas
import sqlite3

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", summary="Register a new user", response_model=schemas.UserOut)
def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: sqlite3.Connection = Depends(database.get_db)
):
    user = auth.get_user_by_email(db, email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.get_password_hash(password)
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (email, hashed_password, full_name) VALUES (?, ?, ?)",
        (email, hashed_pw, full_name)
    )
    db.commit()
    user_id = cursor.lastrowid
    return schemas.UserOut(id=user_id, email=email, full_name=full_name)


@router.post("/token", response_model=schemas.Token, summary="Login for access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: sqlite3.Connection = Depends(database.get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token({"sub": user["email"]})
    return schemas.Token(access_token=access_token)
