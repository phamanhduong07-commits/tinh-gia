from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("", response_model=schemas.ConfigOut)
def get_config(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cfg = db.query(models.Config).filter_by(user_id=current_user.id).first()
    if not cfg:
        cfg = models.Config(user_id=current_user.id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.put("", response_model=schemas.ConfigOut)
def update_config(
    body: schemas.ConfigIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cfg = db.query(models.Config).filter_by(user_id=current_user.id).first()
    if not cfg:
        cfg = models.Config(user_id=current_user.id)
        db.add(cfg)

    cfg.print_cost = body.print_cost
    cfg.make_cost = body.make_cost
    cfg.profit = body.profit
    cfg.waste = body.waste
    db.commit()
    db.refresh(cfg)
    return cfg
