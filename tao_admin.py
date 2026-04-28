"""
Chạy file này để tạo tài khoản Admin đầu tiên:
    python tao_admin.py

Hoặc click đôi vào tao_admin.bat (Windows)
"""
import os
import sys
import getpass

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from backend.database import SessionLocal, engine
    from backend.models import Base, User
    from backend.auth import hash_password

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("=" * 45)
    print("  TẠO TÀI KHOẢN ADMIN – NAM PHƯƠNG")
    print("=" * 45)

    existing = db.query(User).filter_by(role="admin").count()
    if existing:
        print(f"\n⚠  Đã có {existing} Admin trong hệ thống.")
        yn = input("Tạo thêm Admin? (y/N): ").strip().lower()
        if yn != "y":
            db.close()
            return

    print()
    username = input("Username : ").strip()
    if not username:
        print("❌ Username không được để trống"); db.close(); return
    if db.query(User).filter_by(username=username).first():
        print(f"❌ Username '{username}' đã tồn tại"); db.close(); return

    email = input("Email    : ").strip()
    if not email:
        print("❌ Email không được để trống"); db.close(); return
    if db.query(User).filter_by(email=email).first():
        print(f"❌ Email '{email}' đã tồn tại"); db.close(); return

    full_name    = input("Họ tên   : ").strip() or None
    company_name = input("Công ty  : ").strip() or None

    while True:
        pw  = getpass.getpass("Mật khẩu (≥6 ký tự): ")
        pw2 = getpass.getpass("Nhập lại            : ")
        if len(pw) < 6:
            print("⚠  Mật khẩu phải có ít nhất 6 ký tự\n"); continue
        if pw != pw2:
            print("⚠  Mật khẩu không khớp\n"); continue
        break

    user = User(
        email=email, username=username,
        hashed_password=hash_password(pw),
        full_name=full_name, company_name=company_name,
        role="admin", is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    print(f"\n✅ Tạo Admin thành công!")
    print(f"   Username : {user.username}")
    print(f"   Email    : {user.email}")
    print(f"\n👉 Chạy python run.py rồi mở http://localhost:8000/docs để dùng API")
    input("\nNhấn Enter để thoát...")


if __name__ == "__main__":
    main()
