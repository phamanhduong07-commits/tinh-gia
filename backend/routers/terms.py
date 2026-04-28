from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/terms", tags=["Terms"])


@router.get("", response_model=List[schemas.TermOut])
def list_terms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Term)
        .filter_by(user_id=current_user.id)
        .order_by(models.Term.sort_order)
        .all()
    )


@router.put("", response_model=List[schemas.TermOut])
def replace_terms(
    body: schemas.TermsBulk,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db.query(models.Term).filter_by(user_id=current_user.id).delete()
    new_terms = [
        models.Term(user_id=current_user.id, sort_order=i, data=t)
        for i, t in enumerate(body.terms)
    ]
    db.add_all(new_terms)
    db.commit()
    for t in new_terms:
        db.refresh(t)
    return new_terms
