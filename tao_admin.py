import os
import sys

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
    print("  TAO TAI KHOAN ADMIN – NAM PHUONG")
    print("=" * 45)

    existing = db.query(User).filter_by(role="admin").count()
    if existing:
        print(f"\n  Da co {existing} Admin trong he thong.")
        yn = input("  Tao them Admin? (y/N): ").strip().lower()
        if yn != "y":
            db.close()
            input("\nNhan Enter de thoat...")
            return

    print()
    username = input("  Username : ").strip()
    if not username:
        print("  [LOI] Username khong duoc de trong")
        db.close()
        input("\nNhan Enter de thoat...")
        return
    if db.query(User).filter_by(username=username).first():
        print(f"  [LOI] Username '{username}' da ton tai")
        db.close()
        input("\nNhan Enter de thoat...")
        return

    email = input("  Email    : ").strip()
    if not email:
        print("  [LOI] Email khong duoc de trong")
        db.close()
        input("\nNhan Enter de thoat...")
        return
    if db.query(User).filter_by(email=email).first():
        print(f"  [LOI] Email '{email}' da ton tai")
        db.close()
        input("\nNhan Enter de thoat...")
        return

    full_name    = input("  Ho ten   : ").strip() or None
    company_name = input("  Cong ty  : ").strip() or None

    print("  (Mat khau se hien thi khi go - binh thuong)")
    while True:
        pw  = input("  Mat khau (>= 6 ky tu): ").strip()
        if len(pw) < 6:
            print("  [LOI] Mat khau phai co it nhat 6 ky tu")
            continue
        pw2 = input("  Nhap lai mat khau   : ").strip()
        if pw != pw2:
            print("  [LOI] Mat khau khong khop, nhap lai")
            continue
        break

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(pw),
        full_name=full_name,
        company_name=company_name,
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    print()
    print("  [OK] Tao Admin thanh công!")
    print(f"  Username : {user.username}")
    print(f"  Email    : {user.email}")
    print()
    print("  Tiep theo: chay 3_chay_server.bat")
    print("  Sau do mo: http://localhost:8001/docs")
    input("\nNhan Enter de thoat...")


if __name__ == "__main__":
    main()
