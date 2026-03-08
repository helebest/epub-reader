---
name: holo-epub-reader
description: 解析 EPUB 为 LLM 友好的 Markdown/图像块并验证输出完整性。用于需要从 EPUB 提取章节文本、目录结构、图片与 manifest 的任务。
homepage: https://github.com/helebest/holo-epub-reader
---

# Epub Reader

将 EPUB 文件解析为 LLM 友好的文本/图像块，并验证输出。

## 前置条件

1. OpenClaw 全局 Python 环境存在：`$HOME/.openclaw/.venv/bin/python3`
2. EPUB 文件路径可读
3. 输出目录可写

## 使用方法

### 1) 环境检查

```bash
bash {baseDir}/scripts/doctor.sh
```

### 2) 解析 EPUB 文件

```bash
# 解析文件（输出目录必填）
bash {baseDir}/scripts/parse.sh <epub文件路径> <输出目录>
```

### 3) 验证输出

```bash
bash {baseDir}/scripts/validate.sh <输出目录>
```

## 工作流程

1. 运行 `doctor.sh` 检查运行环境
2. 使用 `parse.sh` 解析 EPUB
3. 检查生成的 `content.md`、`manifest.json` 和 `images/`
4. 使用 `validate.sh` 验证输出文件完整性

## 输出格式

默认输出为 Markdown (`content.md`)，包含：
- 文本块
- 标题层级
- 图像（保存到 `images/` 目录）
- 元数据 (`manifest.json`)
