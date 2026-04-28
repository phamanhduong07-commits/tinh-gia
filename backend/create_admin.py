#!/usr/bin/env python3
"""
Script tạo tài khoản Admin đầu tiên từ command line.
Chạy một lần duy nhất khi setup hệ thống.

Cách dùng:
  cd /thư-mục-project
  python -m backend.create_admin
"""
import os
import sys
import getpass


def main():
    print("=" * 50)
    print("  TẠO TÀI KHOẢN ADMIN – NAM PHƯƠNG")
    print("=" * 50)

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        db_url = input("DATABASE_URL (Enter để dùng mặc định localhost): ").strip()
        if not db_url:
            db_url = "postgresql://postgres:postgres@localhost:5432/tinh_gia_db"
        os.environ["DATABASE_URL"] = db_url

    # Import sau khi đặt env
    from backend.database import SessionLocal, engine
    from backend.models import Base, User
    from backend.auth import hash_password

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing_admins = db.query(User).filter_by(role="admin").count()
    if existing_admins > 0:
        print(f"\n⚠️  Đã có {existing_admins} tài khoản Admin trong hệ thống.")
        cont = input("Tiếp tục tạo thêm Admin? (y/N): ").strip().lower()
        if cont != "y":
            db.close()
            return

    print("\nNhập thông tin Admin mới:")
    username = input("  Username: ").strip()
    if not username:
        print("❌ Username không được để trống")
        db.close()
        sys.exit(1)

    if db.query(User).filter_by(username=username).first():
        print(f"❌ Username '{username}' đã tồn tại")
        db.close()
        sys.exit(1)

    email = input("  Email: ").strip()
    if not email:
        print("❌ Email không được để trống")
        db.close()
        sys.exit(1)

    if db.query(User).filter_by(email=email).first():
        print(f"❌ Email '{email}' đã tồn tại")
        db.close()
        sys.exit(1)

    full_name    = input("  Họ tên (có thể bỏ trống): ").strip() or None
    company_name = input("  Tên công ty (có thể bỏ trống): ").strip() or None

    while True:
        password = getpass.getpass("  Mật khẩu (ít nhất 6 ký tự): ")
        if len(password) < 6:
            print("  ⚠️  Mật khẩu quá ngắn, nhập lại")
            continue
        confirm = getpass.getpass("  Xác nhận mật khẩu: ")
        if password != confirm:
            print("  ⚠️  Mật khẩu không khớp, nhập lại")
            continue
        break

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        full_name=full_name,
        company_name=company_name,
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    print(f"\n✅ Tạo Admin thành công!")
    print(f"   ID       : {user.id}")
    print(f"   Username : {user.username}")
    print(f"   Email    : {user.email}")
    print(f"   Role     : {user.role}")
    print(f"\n👉 Đăng nhập tại: POST /api/auth/login")


if __name__ == "__main__":
    main()
