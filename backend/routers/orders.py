from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[schemas.OrderOut])
def list_orders(
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Order).filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Order.cust.ilike(like) | models.Order.item_name.ilike(like) | models.Order.no.ilike(like)
        )
    return query.order_by(models.Order.seq.desc()).all()


@router.post("", response_model=schemas.OrderOut, status_code=201)
def create_order(
    body: schemas.OrderIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = db.query(models.Order).filter_by(
        user_id=current_user.id, no=body.no
    ).first()
    if existing:
        # Upsert: update thay vì báo lỗi (giống JS)
        for k, v in body.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing

    order = models.Order(user_id=current_user.id, **body.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_no}", response_model=schemas.OrderOut)
def update_order(
    order_no: str,
    body: schemas.OrderIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter_by(
        user_id=current_user.id, no=order_no
    ).first()
    if not order:
        raise HTTPException(404, "Không tìm thấy lệnh SX")
    for k, v in body.model_dump().items():
        setattr(order, k, v)
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_no}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_no: str,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter_by(
        user_id=current_user.id, no=order_no
    ).first()
    if not order:
        raise HTTPException(404, "Không tìm thấy lệnh SX")
    order.status = status
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_no}", status_code=204)
def delete_order(
    order_no: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter_by(
        user_id=current_user.id, no=order_no
    ).first()
    if not order:
        raise HTTPException(404, "Không tìm thấy lệnh SX")
    db.delete(order)
    db.commit()
