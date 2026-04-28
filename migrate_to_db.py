#!/usr/bin/env python3
"""
BƯỚC 2: IMPORT DỮ LIỆU VÀO DATABASE
======================================
Chạy script này để import file JSON (từ export_localstorage.js) vào database.

Cách dùng:
  cd /đường/dẫn/project
  python migrate_to_db.py <file_backup.json> --url http://localhost:8000 --token <jwt_token>

Hoặc nếu chạy trực tiếp với DB:
  python migrate_to_db.py <file_backup.json> --direct
"""

import argparse
import json
import sys
import os

import requests


def import_via_api(backup_file: str, api_url: str, token: str):
    """Import dữ liệu qua REST API (khuyến nghị)"""
    with open(backup_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{api_url.rstrip('/')}/api/import"

    print(f"📤 Đang gửi dữ liệu đến {url} ...")
    resp = requests.post(url, json=data, headers=headers, timeout=60)

    if resp.status_code == 200:
        result = resp.json()
        print("✅ Import thành công!")
        print("   Đã import:")
        for k, v in result.get("imported", {}).items():
            print(f"   - {k}: {v} bản ghi")
        if result.get("errors"):
            print("⚠️  Lỗi:")
            for e in result["errors"]:
                print(f"   - {e}")
    else:
        print(f"❌ Lỗi {resp.status_code}: {resp.text}")
        sys.exit(1)


def import_direct(backup_file: str, database_url: str):
    """Import trực tiếp vào database (không cần server chạy)"""
    # Thêm đường dẫn backend vào path
    sys.path.insert(0, os.path.dirname(__file__))
    os.environ["DATABASE_URL"] = database_url

    from backend.database import SessionLocal, engine
    from backend.models import Base, User
    from backend import models
    from backend.auth import hash_password

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Tạo user mặc định nếu chưa có
    user = db.query(User).filter_by(username="admin").first()
    if not user:
        default_pass = input("Nhập mật khẩu cho user admin (mặc định: admin123): ").strip() or "admin123"
        user = User(
            email="admin@company.local",
            username="admin",
            hashed_password=hash_password(default_pass),
            company_name="Nam Phương",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Đã tạo user: admin / {default_pass}")

    with open(backup_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Gọi logic import từ router
    from backend.schemas import BulkImport
    from backend.routers.import_data import bulk_import

    bulk_data = BulkImport(**data)

    class FakeUser:
        id = user.id

    result = bulk_import(bulk_data, db=db, current_user=FakeUser())
    print("✅ Import thành công!")
    print("   Đã import:")
    for k, v in result.imported.items():
        print(f"   - {k}: {v} bản ghi")
    if result.errors:
        print("⚠️  Lỗi:")
        for e in result.errors:
            print(f"   - {e}")

    db.close()


def main():
    parser = argparse.ArgumentParser(description="Import dữ liệu từ localStorage vào database")
    parser.add_argument("backup_file", help="File JSON từ export_localstorage.js")
    parser.add_argument("--url", default="http://localhost:8000", help="URL API server")
    parser.add_argument("--token", help="JWT token (lấy từ đăng nhập)")
    parser.add_argument("--direct", action="store_true", help="Import trực tiếp vào DB")
    parser.add_argument("--db-url", help="DATABASE_URL (dùng với --direct)")
    args = parser.parse_args()

    if not os.path.exists(args.backup_file):
        print(f"❌ Không tìm thấy file: {args.backup_file}")
        sys.exit(1)

    if args.direct:
        db_url = args.db_url or os.getenv("DATABASE_URL", "")
        if not db_url:
            db_url = input("Nhập DATABASE_URL: ").strip()
        import_direct(args.backup_file, db_url)
    else:
        token = args.token
        if not token:
            # Thử đăng nhập để lấy token
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            resp = requests.post(
                f"{args.url.rstrip('/')}/api/auth/login",
                json={"username": username, "password": password},
            )
            if resp.status_code != 200:
                print(f"❌ Đăng nhập thất bại: {resp.text}")
                sys.exit(1)
            token = resp.json()["access_token"]
            print("✅ Đăng nhập thành công")
        import_via_api(args.backup_file, args.url, token)


if __name__ == "__main__":
    main()
