from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/prices", tags=["Paper Prices"])


@router.get("", response_model=schemas.PaperPricesBulk)
def get_prices(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = db.query(models.PaperPrice).filter_by(user_id=current_user.id).all()
    prices: Dict[str, float] = {r.code: r.price_per_kg for r in rows}
    active = next((r.code for r in rows if r.active), None)
    return schemas.PaperPricesBulk(prices=prices, active_paper=active)


@router.put("", response_model=schemas.PaperPricesBulk)
def update_prices(
    body: schemas.PaperPricesBulk,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Xoá tất cả giá cũ của user rồi insert lại
    db.query(models.PaperPrice).filter_by(user_id=current_user.id).delete()
    for code, price in body.prices.items():
        db.add(models.PaperPrice(
            user_id=current_user.id,
            code=code,
            price_per_kg=price,
            active=(code == body.active_paper),
        ))
    db.commit()
    return body
