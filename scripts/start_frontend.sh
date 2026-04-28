#!/bin/bash
cd "$(dirname "$0")/../frontend" || exit 1

if [ ! -d "node_modules" ]; then
  echo "安装依赖..."
  npm install
fi

echo ""
echo "启动前端：http://127.0.0.1:5173"
echo ""
npm run dev
