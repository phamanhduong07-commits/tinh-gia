from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/history", tags=["Calc History"])


@router.get("", response_model=List[schemas.CalcHistoryOut])
def list_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.CalcHistory)
        .filter_by(user_id=current_user.id)
        .order_by(models.CalcHistory.ts.desc())
        .limit(50)
        .all()
    )


@router.post("", response_model=schemas.CalcHistoryOut, status_code=201)
def add_history(
    body: schemas.CalcHistoryIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    h = models.CalcHistory(user_id=current_user.id, **body.model_dump())
    db.add(h)
    # Giữ tối đa 50 bản ghi
    count = db.query(models.CalcHistory).filter_by(user_id=current_user.id).count()
    if count >= 50:
        oldest = (
            db.query(models.CalcHistory)
            .filter_by(user_id=current_user.id)
            .order_by(models.CalcHistory.ts.asc())
            .first()
        )
        if oldest:
            db.delete(oldest)
    db.commit()
    db.refresh(h)
    return h


@router.delete("", status_code=204)
def clear_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db.query(models.CalcHistory).filter_by(user_id=current_user.id).delete()
    db.commit()


@router.delete("/{history_id}", status_code=204)
def delete_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    h = db.query(models.CalcHistory).filter_by(
        id=history_id, user_id=current_user.id
    ).first()
    if h:
        db.delete(h)
        db.commit()
