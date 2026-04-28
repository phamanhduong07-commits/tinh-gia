from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[schemas.CustomerOut])
def list_customers(
    q: Optional[str] = Query(None, description="Tìm theo tên, mã, SĐT"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Customer).filter_by(user_id=current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Customer.name.ilike(like)
            | models.Customer.code.ilike(like)
            | models.Customer.phone.ilike(like)
        )
    return query.order_by(models.Customer.name).all()


@router.post("", response_model=schemas.CustomerOut, status_code=201)
def create_customer(
    body: schemas.CustomerIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = db.query(models.Customer).filter_by(
        user_id=current_user.id, client_id=body.client_id
    ).first()
    if existing:
        raise HTTPException(400, "client_id đã tồn tại")

    cu = models.Customer(user_id=current_user.id, **body.model_dump())
    db.add(cu)
    db.commit()
    db.refresh(cu)
    return cu


@router.put("/{client_id}", response_model=schemas.CustomerOut)
def update_customer(
    client_id: str,
    body: schemas.CustomerIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cu = db.query(models.Customer).filter_by(
        user_id=current_user.id, client_id=client_id
    ).first()
    if not cu:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    for k, v in body.model_dump().items():
        setattr(cu, k, v)
    db.commit()
    db.refresh(cu)
    return cu


@router.delete("/{client_id}", status_code=204)
def delete_customer(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cu = db.query(models.Customer).filter_by(
        user_id=current_user.id, client_id=client_id
    ).first()
    if not cu:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    # Cascade delete products
    db.query(models.Product).filter_by(
        user_id=current_user.id, client_cust_id=client_id
    ).delete()
    db.delete(cu)
    db.commit()
