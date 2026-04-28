from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[schemas.ProductOut])
def list_products(
    cust_id: Optional[str] = Query(None, description="Lọc theo client_cust_id"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Product).filter_by(user_id=current_user.id)
    if cust_id:
        query = query.filter_by(client_cust_id=cust_id)
    return query.order_by(models.Product.name).all()


@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(
    body: schemas.ProductIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = db.query(models.Product).filter_by(
        user_id=current_user.id, client_id=body.client_id
    ).first()
    if existing:
        raise HTTPException(400, "client_id đã tồn tại")

    # Resolve customer FK
    customer_id = None
    if body.client_cust_id:
        cu = db.query(models.Customer).filter_by(
            user_id=current_user.id, client_id=body.client_cust_id
        ).first()
        if cu:
            customer_id = cu.id

    prod = models.Product(
        user_id=current_user.id,
        customer_id=customer_id,
        **body.model_dump(),
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


@router.put("/{client_id}", response_model=schemas.ProductOut)
def update_product(
    client_id: str,
    body: schemas.ProductIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prod = db.query(models.Product).filter_by(
        user_id=current_user.id, client_id=client_id
    ).first()
    if not prod:
        raise HTTPException(404, "Không tìm thấy mã hàng")

    customer_id = None
    if body.client_cust_id:
        cu = db.query(models.Customer).filter_by(
            user_id=current_user.id, client_id=body.client_cust_id
        ).first()
        if cu:
            customer_id = cu.id

    for k, v in body.model_dump().items():
        setattr(prod, k, v)
    prod.customer_id = customer_id
    db.commit()
    db.refresh(prod)
    return prod


@router.delete("/{client_id}", status_code=204)
def delete_product(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prod = db.query(models.Product).filter_by(
        user_id=current_user.id, client_id=client_id
    ).first()
    if not prod:
        raise HTTPException(404, "Không tìm thấy mã hàng")
    db.delete(prod)
    db.commit()
