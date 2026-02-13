---
name: epub-reader
description: 将 EPUB 文件解析为 LLM 友好的文本/图像块，并验证输出。默认输出为 Markdown。
homepage: https://github.com/helebest/epub-reader
metadata:
  {
    "openclaw":
      {
        "emoji": "📚",
        "requires": { "bins": ["python3"] },
        "install": [],
      },
  }
---

# Epub Reader

将 EPUB 文件解析为 LLM 友好的文本/图像块，并验证输出。默认输出为 Markdown。

## 前置条件

1. Python 3 已安装（系统自带）
2. EPUB 文件路径

## 使用方法

### 解析 EPUB 文件

```bash
# 解析文件（必须指定输出目录）
bash {baseDir}/scripts/parse.sh <epub文件路径> <输出目录>
```

### 验证输出

```bash
bash {baseDir}/scripts/validate.sh <输出目录>
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
