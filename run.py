"""
Chạy file này để khởi động server:
    python run.py

Hoặc click đôi vào run.bat (Windows)
"""
import os
import sys

# Force UTF-8 output on Windows to support Vietnamese characters
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Đảm bảo thư mục gốc project luôn trong Python path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import uvicorn

if __name__ == "__main__":
    print("=" * 55)
    print("  NAM PHUONG – TINH GIA SERVER")
    print("=" * 55)
    print(f"  Thư mục: {ROOT}")
    print(f"  API:     http://localhost:8002")
    print(f"  Docs:    http://localhost:8002/docs")
    print("  Nhấn Ctrl+C để tắt")
    print("=" * 55)
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        reload_dirs=[ROOT],
    )
