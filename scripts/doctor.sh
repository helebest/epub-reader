#!/usr/bin/env bash
# 环境诊断脚本
# 用法: bash doctor.sh

set -euo pipefail

PYTHON_CMD="$HOME/.openclaw/.venv/bin/python3"

if [ ! -x "$PYTHON_CMD" ]; then
    echo "错误: 未找到可执行 Python: $PYTHON_CMD"
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

exec "$PYTHON_CMD" -m holo_epub_reader.cli doctor
