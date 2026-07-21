#!/usr/bin/env python3
"""本地一键启动提示（v2）。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    print("短镜 v2")
    print("1) 确保 MySQL 已启动，库 ai_video_maker 存在")
    print("2) 后端: cd backend && cp -n .env.example .env && uvicorn main:app --reload --port 8000")
    print("3) 前端: cd frontend && npm start")
    print()
    if "--backend" in sys.argv:
        subprocess.check_call(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=ROOT / "backend",
        )


if __name__ == "__main__":
    main()
