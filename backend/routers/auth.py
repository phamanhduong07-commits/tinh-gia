from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import (
    create_access_token, get_current_user,
    hash_password, verify_password,
)
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/setup", response_model=schemas.Token, summary="Tạo Admin đầu tiên (chỉ khi DB trống)")
def first_time_setup(body: schemas.UserCreate, db: Session = Depends(get_db)):
    """Chỉ hoạt động khi chưa có user nào trong hệ thống."""
    if db.query(models.User).count() > 0:
        raise HTTPException(
            status_code=403,
            detail="Hệ thống đã được khởi tạo. Admin dùng /admin/users để tạo thêm user.",
        )
    user = models.User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        company_name=body.company_name,
        role="admin",  # người đầu tiên luôn là admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=schemas.UserOut.model_validate(user),
    )


@router.post("/login", response_model=schemas.Token)
def login(body: schemas.UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == body.username)
        .first()
    )
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai username hoặc mật khẩu",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")

    token = create_access_token({"sub": user.id})
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=schemas.UserOut.model_validate(user),
    )


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.UserOut, summary="Cập nhật thông tin cá nhân")
def update_me(
    body: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # User thường không được tự đổi role
    if body.email:
        taken = db.query(models.User).filter(
            models.User.email == body.email,
            models.User.id != current_user.id,
        ).first()
        if taken:
            raise HTTPException(400, "Email đã được sử dụng")
        current_user.email = body.email
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.company_name is not None:
        current_user.company_name = body.company_name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", summary="Đổi mật khẩu của chính mình")
def change_password(
    body: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng")
    if len(body.new_password) < 6:
        raise HTTPException(400, "Mật khẩu mới phải có ít nhất 6 ký tự")
    current_user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"detail": "Đổi mật khẩu thành công"}
