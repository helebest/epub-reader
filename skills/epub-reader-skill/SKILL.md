---
name: epub-reader-skill
description: Use when you need to parse EPUB files into LLM-friendly text/image blocks, run the epub-reader CLI with uv isolation, validate outputs, or explain the output schema and verification steps.
---

# Epub Reader Skill (OpenClaw 本地化版本)

## 描述

将 EPUB 文件解析为 LLM 友好的文本/图像块，并验证输出。默认输出为 Markdown。

## 前置条件

1. 已安装 uv 包管理器
2. EPUB 文件路径

## 使用方法

### 解析 EPUB 文件

```bash
# 解析文件（默认输出到 ./output）
bash /mnt/usb/projects/epub-reader/skills/epub-reader-skill/scripts/parse.sh <epub文件路径>

# 指定输出目录
bash /mnt/usb/projects/epub-reader/skills/epub-reader-skill/scripts/parse.sh <epub文件路径> <输出目录>
```

### 验证输出

```bash
bash /mnt/usb/projects/epub-reader/skills/epub-reader-skill/scripts/validate.sh <输出目录>
```

## 工作流程

1. 使用 `parse.sh` 解析 EPUB
2. 检查生成的 `content.md`、`manifest.json` 和 `images/`
3. 使用 `validate.sh` 验证文件完整性和数量

## 输出格式

默认输出为 Markdown (`content.md`)，包含：
- 文本块
- 标题层级
- 图像（保存到 `images/` 目录）
- 元数据 (`manifest.json`)

## OpenClaw 集成

此 skill 已本地化为 OpenClaw 兼容格式：
- ✅ bash 脚本直接调用
- ✅ 无需安装（使用 uv run）
- ✅ 符合 OpenClaw skill 结构规范

## 注意事项

- 使用 `uv run` 保持依赖隔离
- 离线模式下也可运行
- 建议先验证输出再使用
