from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_admin_user, get_current_user
from ..database import get_db

router = APIRouter(prefix="/prices", tags=["Paper Prices"])


@router.get("", response_model=schemas.PaperPricesBulk, summary="Xem giá giấy (mọi user)")
def get_prices(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    rows = db.query(models.PaperPrice).all()
    prices: Dict[str, float] = {r.code: r.price_per_kg for r in rows}
    active = next((r.code for r in rows if r.active), None)
    return schemas.PaperPricesBulk(prices=prices, active_paper=active)


@router.put("", response_model=schemas.PaperPricesBulk, summary="Cập nhật giá giấy (chỉ Admin)")
def update_prices(
    body: schemas.PaperPricesBulk,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user),
):
    existing = {r.code: r for r in db.query(models.PaperPrice).all()}
    for code, price in body.prices.items():
        if code in existing:
            existing[code].price_per_kg = price
            existing[code].active = (code == body.active_paper)
            existing[code].updated_by = admin.id
        else:
            db.add(models.PaperPrice(
                code=code,
                price_per_kg=price,
                active=(code == body.active_paper),
                updated_by=admin.id,
            ))
    # Xoá các mã không còn trong danh sách gửi lên
    for code, row in existing.items():
        if code not in body.prices:
            db.delete(row)
    db.commit()
    return body
