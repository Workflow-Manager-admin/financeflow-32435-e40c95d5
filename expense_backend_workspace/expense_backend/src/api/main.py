from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import initialize_database
from . import routes_auth, routes_categories, routes_expenses

app = FastAPI(
    title="Expense Tracker API",
    description=(
        "Backend API for managing, categorizing, and analyzing expenses. "
        "Provides authentication, CRUD operations, monthly summaries, and OpenAPI docs."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "User registration and login"},
        {"name": "Categories", "description": "User-specific categories for expenses"},
        {"name": "Expenses", "description": "Adding, editing, listing, and deleting expenses"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    initialize_database()


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


app.include_router(routes_auth.router)
app.include_router(routes_categories.router)
app.include_router(routes_expenses.router)
