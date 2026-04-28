from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/presets", tags=["Presets"])


@router.get("", response_model=List[schemas.PresetOut])
def list_presets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Preset).filter_by(user_id=current_user.id).all()


@router.put("", response_model=List[schemas.PresetOut])
def replace_presets(
    body: schemas.PresetsBulk,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db.query(models.Preset).filter_by(user_id=current_user.id).delete()
    new_presets = [
        models.Preset(user_id=current_user.id, data=p)
        for p in body.presets
    ]
    db.add_all(new_presets)
    db.commit()
    for p in new_presets:
        db.refresh(p)
    return new_presets
