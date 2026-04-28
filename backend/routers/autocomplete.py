from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/autocomplete", tags=["AutoComplete"])


@router.get("", response_model=Dict[str, Any])
def get_autocomplete(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = db.query(models.AutoComplete).filter_by(user_id=current_user.id).all()
    return {r.name: r.data for r in rows}


@router.put("", response_model=Dict[str, Any])
def sync_autocomplete(
    body: schemas.AutoCompleteBulk,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = {
        r.name: r
        for r in db.query(models.AutoComplete).filter_by(user_id=current_user.id).all()
    }
    for name, data in body.entries.items():
        if name in existing:
            existing[name].data = data
        else:
            db.add(models.AutoComplete(user_id=current_user.id, name=name, data=data))

    # Giữ tối đa 200 entries
    all_rows = db.query(models.AutoComplete).filter_by(user_id=current_user.id).all()
    if len(all_rows) > 200:
        to_delete = sorted(all_rows, key=lambda r: r.id)[: len(all_rows) - 200]
        for r in to_delete:
            db.delete(r)

    db.commit()
    return body.entries
