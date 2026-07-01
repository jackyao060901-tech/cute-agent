"""可选 PDF 导出:用本机 Chromium 把 HTML 打印成 PDF。

无 Chromium 时抛清晰错误(降级建议:保存 HTML 后用浏览器"打印为 PDF")。
不引入第三方依赖。
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import zlib


class PdfExportError(RuntimeError):
    pass


def pdf_digit_runs(pdf_path: str) -> set[str]:
    """从 PDF 内容流(FlateDecode)提取可读的数字游程集合(stdlib,尽力而为)。

    用途:审计 PDF 文本层是否含关键数值。数字游程对字距(kerning)拆分稳健;
    字母/中文因字形子集编码不适用于此法,故本校验只覆盖数字类指标。
    """
    raw = open(pdf_path, "rb").read()
    text = b""
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        try:
            text += zlib.decompress(m.group(1))
        except Exception:
            pass
    ascii_digits = bytes(b if 48 <= b <= 57 else 32 for b in text).decode("latin1")
    return set(re.findall(r"\d+", ascii_digits))


def find_chromium() -> str | None:
    """按优先级查找 Chromium 可执行文件。"""
    if os.environ.get("CHROME_BIN") and os.path.exists(os.environ["CHROME_BIN"]):
        return os.environ["CHROME_BIN"]
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        p = shutil.which(name)
        if p:
            return p
    # Playwright 预装路径(远程执行环境)
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    if os.path.isdir(base):
        import glob
        for pat in ("chromium-*/chrome-linux/chrome", "chromium-*/chrome-linux/headless_shell"):
            hits = sorted(glob.glob(os.path.join(base, pat)))
            if hits:
                return hits[-1]
    return None


def html_to_pdf(html: str, pdf_path: str, chromium: str | None = None) -> str:
    """把 HTML 字符串渲染为 PDF 文件,返回 pdf_path。"""
    exe = chromium or find_chromium()
    if not exe:
        raise PdfExportError(
            "未找到 Chromium,无法直接导出 PDF。请设置 CHROME_BIN,"
            "或保存 --html 输出后用浏览器'打印为 PDF'。"
        )
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        html_path = f.name
    try:
        cmd = [
            exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}", f"file://{html_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise PdfExportError(f"Chromium 未产出 PDF:{r.stderr[-300:]}")
    finally:
        os.unlink(html_path)
    return pdf_path
