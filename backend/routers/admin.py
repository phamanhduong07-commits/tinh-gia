"""
Admin-only endpoints: quản lý danh sách người dùng.
Tất cả endpoints này yêu cầu role = "admin".
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_admin_user, hash_password
from ..database import get_db
from ..models import Customer, Order

router = APIRouter(prefix="/admin", tags=["Admin – Quản lý người dùng"])


@router.get("/users", response_model=List[schemas.UserOut], summary="Danh sách tất cả người dùng")
def list_users(
    q: Optional[str] = Query(None, description="Tìm theo username, email, họ tên"),
    role: Optional[str] = Query(None, description="Lọc theo role: admin | user"),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
):
    query = db.query(models.User)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.User.username.ilike(like)
            | models.User.email.ilike(like)
            | models.User.full_name.ilike(like)
        )
    if role:
        query = query.filter_by(role=role)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    return query.order_by(models.User.created_at.desc()).all()


@router.post("/users", response_model=schemas.UserOut, status_code=201, summary="Tạo người dùng mới")
def create_user(
    body: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(400, "Email đã được sử dụng")
    if db.query(models.User).filter(models.User.username == body.username).first():
        raise HTTPException(400, "Username đã được sử dụng")
    if body.role not in ("admin", "user"):
        raise HTTPException(400, "role phải là 'admin' hoặc 'user'")
    if len(body.password) < 6:
        raise HTTPException(400, "Mật khẩu phải có ít nhất 6 ký tự")

    user = models.User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        company_name=body.company_name,
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=schemas.UserOut, summary="Chi tiết một người dùng")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return user


@router.put("/users/{user_id}", response_model=schemas.UserOut, summary="Cập nhật thông tin người dùng")
def update_user(
    user_id: int,
    body: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user),
):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "Không tìm thấy người dùng")

    # Không cho admin tự hạ cấp chính mình
    if user.id == admin.id and body.role == "user":
        raise HTTPException(400, "Không thể tự hạ quyền Admin của chính mình")

    if body.email is not None:
        taken = db.query(models.User).filter(
            models.User.email == body.email,
            models.User.id != user_id,
        ).first()
        if taken:
            raise HTTPException(400, "Email đã được sử dụng")
        user.email = body.email

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.company_name is not None:
        user.company_name = body.company_name
    if body.role is not None:
        if body.role not in ("admin", "user"):
            raise HTTPException(400, "role phải là 'admin' hoặc 'user'")
        user.role = body.role
    if body.is_active is not None:
        if user.id == admin.id and not body.is_active:
            raise HTTPException(400, "Không thể tự khóa tài khoản Admin của chính mình")
        user.is_active = body.is_active

    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reset-password", summary="Reset mật khẩu người dùng")
def reset_password(
    user_id: int,
    body: schemas.AdminResetPassword,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "Không tìm thấy người dùng")
    if len(body.new_password) < 6:
        raise HTTPException(400, "Mật khẩu phải có ít nhất 6 ký tự")
    user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"detail": f"Đã reset mật khẩu cho user '{user.username}'"}


@router.patch("/users/{user_id}/toggle-active", response_model=schemas.UserOut, summary="Khoá / Mở khoá tài khoản")
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user),
):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "Không tìm thấy người dùng")
    if user.id == admin.id:
        raise HTTPException(400, "Không thể tự khóa tài khoản của chính mình")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204, summary="Xoá người dùng")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user),
):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "Không tìm thấy người dùng")
    if user.id == admin.id:
        raise HTTPException(400, "Không thể xoá chính tài khoản Admin đang đăng nhập")
    db.delete(user)
    db.commit()


@router.get("/stats", summary="Thống kê tổng quan hệ thống")
def system_stats(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
):
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter_by(is_active=True).count()
    admin_count = db.query(models.User).filter_by(role="admin").count()
    total_customers = db.query(Customer).count()
    total_orders = db.query(Order).count()
    return {
        "users": {"total": total_users, "active": active_users, "admins": admin_count},
        "customers": total_customers,
        "orders": total_orders,
    }
