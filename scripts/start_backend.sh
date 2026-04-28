#!/bin/bash
cd "$(dirname "$0")/../backend" || exit 1

if [ ! -d ".venv" ]; then
  echo "创建虚拟环境..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt
echo ""
echo "启动后端：http://127.0.0.1:6965"
echo "Swagger：http://127.0.0.1:6965/docs"
echo ""
fastapi dev app/main.py
