#!/bin/bash
# ═══════════════════════════════════════════════════
#  Blog 一键部署脚本
#  用法: bash deploy.sh
# ═══════════════════════════════════════════════════
set -e

echo "========================================"
echo "  Blog 部署脚本"
echo "========================================"

# ── 1. 检查 .env ──
if [ ! -f .env ]; then
    echo ""
    echo "[!] 未找到 .env 文件！"
    echo "    请先复制模板并填入真实值："
    echo "    cp .env.production .env"
    echo "    vim .env   # 修改 SECRET_KEY 和服务器 IP"
    echo ""
    exit 1
fi

# ── 2. 检查 dist ──
if [ ! -f frontend/dist/index.html ]; then
    echo ""
    echo "[!] 未找到前端构建产物 frontend/dist/"
    echo "    正在构建前端..."
    cd frontend
    npm ci --silent
    npm run build
    cd ..
fi

echo "[OK] 前端构建产物就绪"

# ── 3. 构建并启动 ──
echo ""
echo "正在构建 Docker 镜像并启动服务..."
docker compose up -d --build

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "  前端:  http://你的服务器IP"
echo "  后端:  http://你的服务器IP:6965"
echo ""
echo "  管理后台: http://你的服务器IP/admin"
echo "  默认管理员: minlan01"
echo ""
echo "  查看日志: docker compose logs -f"
echo "  停止服务: docker compose down"
echo ""
echo "  ⚠️  重要: 登录后请立即修改管理员密码！"
echo "========================================"
