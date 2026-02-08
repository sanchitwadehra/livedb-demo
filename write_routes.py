"""Write endpoints — SQLAlchemy writes + LiveDB reads.

Demonstrates Code Time vs Run Time behavior from SPEC.md:
- Reads-first pattern (5.6 best practice)
- Write-before-read (stale preview at code time)
- Uncommitted write (stale in BOTH contexts)
"""

from datetime import datetime
from fastapi import APIRouter
from livedb import db
from models import SessionLocal, User, Order
from seed_db import seed

router = APIRouter(prefix="/api")


# =========================================================================
# GOOD: Reads first, writes last (5.6 best practice)
# =========================================================================
@router.post("/orders/create")
async def create_order(
    user_id: int = 1,
    product: str = "Widget",
    total: float = 59.99,
):
    # === READS FIRST — LiveDB preview works here ===
    # Cursor here → preview shows user 1 (Alice)
    user = db.table("users").filter(f"id = {user_id}")
    user_row = user.fetchone()
    if not user_row:
        return {"error": "User not found"}

    # Cursor here → preview shows existing orders
    existing = db.table("orders").filter(f"user_id = {user_id}")

    # === WRITES LAST — SQLAlchemy, not LiveDB ===
    session = SessionLocal()
    new_order = Order(
        user_id=user_id, product=product, total=total,
        created_at=datetime.now().isoformat(),
    )
    session.add(new_order)
    session.commit()
    order_id = new_order.id
    session.close()

    return {
        "created": {"id": order_id, "product": product, "total": total},
        "user": user_row,
        "previous_order_count": len(existing.fetchall()),
    }


# =========================================================================
# BAD: Write before read (stale preview at code time)
# =========================================================================
@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int = 1):
    # WRITE FIRST — SQLAlchemy executes at run time, not code time
    session = SessionLocal()
    user_obj = session.query(User).get(user_id)
    if not user_obj:
        session.close()
        return {"error": "User not found"}
    user_obj.status = "inactive"
    session.commit()
    session.close()

    # READ AFTER COMMITTED WRITE
    # CODE TIME: preview shows OLD status (write didn't execute)
    # RUN TIME:  write committed, LiveDB sees status='inactive'
    user = db.table("users").filter(f"id = {user_id}")
    return {"user": user.fetchone(), "note": "write-before-read"}


# =========================================================================
# BAD: Uncommitted write before read
# =========================================================================
@router.post("/users/{user_id}/deactivate-broken")
async def deactivate_broken(user_id: int = 1):
    session = SessionLocal()
    user_obj = session.query(User).get(user_id)
    if not user_obj:
        session.close()
        return {"error": "User not found"}
    user_obj.status = "BROKEN"
    # NO session.commit() — change only visible inside this session

    # LiveDB reads from DB — can't see uncommitted changes
    # CODE TIME: write didn't execute → old status
    # RUN TIME:  write not committed → old status too!
    user = db.table("users").filter(f"id = {user_id}")
    result = user.fetchone()

    session.rollback()
    session.close()
    return {"user": result, "note": "uncommitted write — status unchanged"}


# =========================================================================
# GOOD: Reactivate user (undo deactivate)
# =========================================================================
@router.post("/users/{user_id}/activate")
async def activate_user(user_id: int = 1):
    session = SessionLocal()
    user_obj = session.query(User).get(user_id)
    if not user_obj:
        session.close()
        return {"error": "User not found"}
    user_obj.status = "active"
    session.commit()
    session.close()

    user = db.table("users").filter(f"id = {user_id}")
    return {"user": user.fetchone()}


# =========================================================================
# Reset database to original state
# =========================================================================
@router.post("/reset")
async def reset_data():
    seed()
    return {"status": "Database reset to original state"}
