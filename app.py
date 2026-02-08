"""LiveDB Demo — FastAPI app matching SPEC.md Section 6.

Open this file in VS Code with the LiveDB extension active.
Place cursor on any db.* line to see live preview.

Reads:  LiveDB (via DuckDB sqlite_scanner)
Writes: SQLAlchemy (direct SQLite connection)

Run:  uvicorn app:app --reload
Open: http://localhost:8000
"""

import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from livedb import db
from write_routes import router as write_router

_dir = os.path.dirname(__file__)
app = FastAPI(title="LiveDB Demo API")
app.include_router(write_router)
db.connect(os.path.join(_dir, "app.sqlite"))

DEFAULT_LIMIT = 5
BASE_PRICE = 50
PREMIUM_THRESHOLD = BASE_PRICE * 4  # 5.8 computes: 200


@app.get("/", response_class=HTMLResponse)
async def frontend():
    html = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html) as f:
        return f.read()


# =========================================================================
# READ endpoints — LiveDB previews work on all of these
# =========================================================================

@app.get("/api/users")
async def list_users(min_age: int = 18, status: str = "active", limit: int = 10):
    users = db.table("users") \
        .filter(f"age >= {min_age}") \
        .filter(f"status = '{status}'") \
        .limit(limit)
    return {"users": users.fetchall()}


@app.get("/api/users/{user_id}")
async def get_user(user_id: int = 1):
    user = db.table("users").filter(f"id = {user_id}")
    return {"user": user.fetchone()}


@app.get("/api/orders")
async def list_orders(min_total: float = 50.0, max_total: float = 500.0):
    orders = db.table("orders") \
        .filter(f"total >= {min_total}") \
        .filter(f"total <= {max_total}")
    return {"orders": orders.fetchall()}


@app.get("/api/users/{user_id}/orders")
async def get_user_orders(user_id: int = 1):
    user = db.table("users").filter(f"id = {user_id}")
    orders = db.table("orders").filter(f"user_id = {user_id}")
    return {"user": user.fetchone(), "orders": orders.fetchall()}


@app.get("/api/orders/premium")
async def premium_orders():
    orders = db.table("orders") \
        .filter(f"total >= {PREMIUM_THRESHOLD}")
    return {"premium_orders": orders.fetchall()}


@app.get("/api/dashboard")
async def dashboard(request: Request):
    user_id = request.query_params.get("user_id")  # @preview: 1
    period = request.query_params.get("period")     # @preview: "2026"

    user = db.table("users").filter(f"id = {user_id}")
    orders = db.table("orders") \
        .filter(f"user_id = {user_id}") \
        .filter(f"created_at >= '{period}'")
    return {"user": user.fetchone(), "recent_orders": orders.fetchall()}
