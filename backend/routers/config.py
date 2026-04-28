from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_admin_user, get_current_user
from ..database import get_db

router = APIRouter(prefix="/config", tags=["Config"])


def _get_or_create(db: Session) -> models.Config:
    cfg = db.query(models.Config).first()
    if not cfg:
        cfg = models.Config()
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.get("", response_model=schemas.ConfigOut, summary="Xem cấu hình chi phí (mọi user)")
def get_config(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return _get_or_create(db)


@router.put("", response_model=schemas.ConfigOut, summary="Cập nhật cấu hình chi phí (chỉ Admin)")
def update_config(
    body: schemas.ConfigIn,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user),
):
    cfg = _get_or_create(db)
    cfg.print_cost = body.print_cost
    cfg.make_cost = body.make_cost
    cfg.profit = body.profit
    cfg.waste = body.waste
    cfg.updated_by = admin.id
    db.commit()
    db.refresh(cfg)
    return cfg
