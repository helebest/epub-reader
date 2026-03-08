# holo-epub-reader

Parse EPUB files into LLM-friendly text and image blocks.

## 开发

```bash
# 安装依赖（含测试工具）
uv sync --extra dev

# 运行测试（覆盖率门禁 90%+）
uv run pytest --cov=holo_epub_reader --cov-report=term-missing --cov-fail-under=90
```

## 部署

```bash
# 部署到 OpenClaw skills 目录
./openclaw_deploy_skill.sh <target-path>
```

部署后的目录结构：

```
skill-name/
├── SKILL.md
├── holo_epub_reader/
│   ├── cli.py
│   ├── doctor.py
│   ├── reader.py
│   └── ...
└── scripts/
    ├── doctor.sh
    ├── parse.sh
    └── validate.sh
```

## 使用

```bash
# 前置检查（必须先通过）
bash <skill-path>/scripts/doctor.sh

# 解析 EPUB（输出目录必填）
bash <skill-path>/scripts/parse.sh <epub文件路径> <输出目录>

# 验证输出
bash <skill-path>/scripts/validate.sh <输出目录>
```

也可直接使用 Python CLI：

```bash
$HOME/.openclaw/.venv/bin/python3 -m holo_epub_reader.cli doctor
$HOME/.openclaw/.venv/bin/python3 -m holo_epub_reader.cli parse <epub文件路径> --out <输出目录>
$HOME/.openclaw/.venv/bin/python3 -m holo_epub_reader.cli validate <输出目录>
```

## 输出

默认输出为 Markdown (`content.md`)，包含：
- 文本块
- 标题层级
- 图像（保存到 `images/` 目录）
- 元数据 (`manifest.json`)
