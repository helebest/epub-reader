from __future__ import annotations

import json
from pathlib import Path
import zipfile

import pytest

from holo_epub_reader.reader import EpubParseError, parse_epub, validate_output


def _create_epub(
    tmp_path: Path,
    *,
    body: str,
    include_container: bool = True,
    include_opf: bool = True,
    include_image_tag: bool = True,
    include_image_file: bool = True,
) -> Path:
    root = tmp_path / "sample"
    meta_inf = root / "META-INF"
    oebps = root / "OEBPS"
    images = oebps / "images"
    meta_inf.mkdir(parents=True)
    images.mkdir(parents=True)

    if include_container:
        container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml" />
  </rootfiles>
</container>
"""
        (meta_inf / "container.xml").write_text(container_xml, encoding="utf-8")

    if include_opf:
        image_item = (
            '<item id="img1" href="images/pic.jpg" media-type="image/jpeg" />'
            if include_image_tag
            else ""
        )
        content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Sample</dc:title>
    <dc:creator>Tester</dc:creator>
  </metadata>
  <manifest>
    <item id="chap1" href="chapter1.xhtml" media-type="application/xhtml+xml" />
    {image_item}
  </manifest>
  <spine toc="ncx">
    <itemref idref="chap1" />
  </spine>
</package>
"""
        (oebps / "content.opf").write_text(content_opf, encoding="utf-8")

    image_html = '<img src="images/pic.jpg" alt="A pic" />' if include_image_tag else ""
    chapter1 = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>未知</title>
  </head>
  <body>
    {body}
    {image_html}
  </body>
</html>
"""
    (oebps / "chapter1.xhtml").write_text(chapter1, encoding="utf-8")

    if include_image_file:
        (images / "pic.jpg").write_bytes(b"\x00\x01\x02")

    epub_path = tmp_path / "sample.epub"
    with zipfile.ZipFile(epub_path, "w") as zf:
        for path in root.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(root))

    return epub_path


def test_parse_and_validate_happy_path(tmp_path: Path) -> None:
    body = """
    <h1>Chapter One</h1>
    <h2>Section A</h2>
    <h2>Contents</h2>
    <p>Hello world.</p>
    <ol>
      <li>First item</li>
      <li>Second item</li>
    </ol>
    """
    epub_path = _create_epub(tmp_path, body=body)
    out_dir = tmp_path / "out"

    manifest = parse_epub(epub_path, out_dir, include_images=True)

    assert (out_dir / "content.md").exists()
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "images" / "OEBPS" / "images" / "pic.jpg").exists()
    assert manifest["images_extracted"] is True

    ok, errors = validate_output(out_dir)
    assert ok, errors

    content = (out_dir / "content.md").read_text(encoding="utf-8")
    assert "## Chapter One" in content
    assert "## 目录" in content
    assert "- [Chapter One]" in content
    assert "  - [Section A]" in content
    assert "#### Contents" in content
    assert "- [Contents]" not in content
    assert "1. First item" in content
    assert "2. Second item" in content
    assert "![A pic]" in content


def test_parse_supports_blockquote_pre_and_unordered_list(tmp_path: Path) -> None:
    body = """
    <h1>Chapter One</h1>
    <blockquote>line1\nline2</blockquote>
    <pre>code\nline</pre>
    <ul><li>bullet</li></ul>
    """
    epub_path = _create_epub(tmp_path, body=body)
    out_dir = tmp_path / "out"

    parse_epub(epub_path, out_dir, include_images=True)
    content = (out_dir / "content.md").read_text(encoding="utf-8")

    assert "> line1" in content
    assert "```" in content
    assert "- bullet" in content


def test_parse_without_image_extraction_sets_manifest_flag(tmp_path: Path) -> None:
    body = "<h1>Chapter One</h1><p>Text</p>"
    epub_path = _create_epub(tmp_path, body=body, include_image_tag=True, include_image_file=False)
    out_dir = tmp_path / "out"

    manifest = parse_epub(epub_path, out_dir, include_images=False)

    assert manifest["images_extracted"] is False
    assert manifest["images"] == []

    ok, errors = validate_output(out_dir)
    assert ok, errors


def test_parse_collects_missing_images(tmp_path: Path) -> None:
    body = "<h1>Chapter One</h1><p>Text</p>"
    epub_path = _create_epub(tmp_path, body=body, include_image_tag=True, include_image_file=False)
    out_dir = tmp_path / "out"

    manifest = parse_epub(epub_path, out_dir, include_images=True)

    assert manifest["missing_images"] == ["OEBPS/images/pic.jpg"]
    assert manifest["images"] == []


def test_parse_chunks_long_unspaced_text(tmp_path: Path) -> None:
    long_word = "a" * 25
    body = f"<h1>Chapter One</h1><p>{long_word}</p>"
    epub_path = _create_epub(tmp_path, body=body, include_image_tag=False)
    out_dir = tmp_path / "out"

    parse_epub(epub_path, out_dir, include_images=False, max_chunk_chars=10)
    content = (out_dir / "content.md").read_text(encoding="utf-8")

    assert "aaaaaaaaaa" in content
    assert "aaaaa" in content


def test_parse_raises_when_container_missing(tmp_path: Path) -> None:
    body = "<h1>Chapter One</h1><p>Text</p>"
    epub_path = _create_epub(
        tmp_path,
        body=body,
        include_container=False,
        include_opf=True,
        include_image_tag=False,
    )

    with pytest.raises(EpubParseError, match="Missing META-INF/container.xml"):
        parse_epub(epub_path, tmp_path / "out")


def test_parse_raises_when_opf_missing(tmp_path: Path) -> None:
    body = "<h1>Chapter One</h1><p>Text</p>"
    epub_path = _create_epub(
        tmp_path,
        body=body,
        include_container=True,
        include_opf=False,
        include_image_tag=False,
    )

    with pytest.raises(EpubParseError, match="Missing OPF file"):
        parse_epub(epub_path, tmp_path / "out")


def test_validate_output_missing_content_file(tmp_path: Path) -> None:
    ok, errors = validate_output(tmp_path)
    assert not ok
    assert "content.md not found" in errors


def test_validate_output_invalid_manifest_json(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)
    (out_dir / "content.md").write_text("ok", encoding="utf-8")
    (out_dir / "manifest.json").write_text("{invalid", encoding="utf-8")

    ok, errors = validate_output(out_dir)
    assert not ok
    assert "manifest.json is invalid JSON" in errors


def test_validate_output_reports_missing_image_file(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)
    (out_dir / "content.md").write_text("ok", encoding="utf-8")
    payload = {
        "images_extracted": True,
        "images": ["images/missing.jpg"],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )

    ok, errors = validate_output(out_dir)
    assert not ok
    assert "Missing image file: images/missing.jpg" in errors
