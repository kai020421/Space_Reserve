from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix="/debug", tags=["Debug (delete later)"])

@router.get("/validate")
def validate(limit: int = Query(...)):
    return {"data": limit}

@router.get("/conflict")
def conflict():
    raise HTTPException(status_code=409, detail="This slot is already booked")

@router.get("/crash")
def crash():
    raise RuntimeError("test crash")

@router.get("/db")
def database_test(db: Session = Depends(get_db)):
    value = db.execute(text("SELECT 1")).scalar_one()
    return {"data": {"database": "connected", "test_query": value}}
