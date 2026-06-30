"""配置与密钥读取.

原则(见 CLAUDE.md):代码绝不硬编码 Key,一律从环境变量读取。
可选地从仓库根的 .env 文件加载(jack 同意 Key 在仓库转 private 后入库;
在此之前 .env 不提交)。这里用极简解析,不引入第三方依赖。
"""
from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """把 .env 里的 KEY=VALUE 注入 os.environ(已存在的不覆盖)。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        os.environ.setdefault(key, val)


_load_dotenv(_REPO_ROOT / ".env")


class ConfigError(RuntimeError):
    """缺少必要配置时抛出。"""


def llmquant_api_key() -> str:
    key = os.environ.get("LLMQUANT_API_KEY")
    if not key:
        raise ConfigError(
            "缺少 LLMQUANT_API_KEY。请 `export LLMQUANT_API_KEY=...` 或写入仓库根 .env。"
        )
    return key


def deepseek_api_key() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise ConfigError(
            "缺少 DEEPSEEK_API_KEY。请 `export DEEPSEEK_API_KEY=...` 或写入仓库根 .env。"
        )
    return key


LLMQUANT_BASE_URL = os.environ.get("LLMQUANT_BASE_URL", "https://api.llmquantdata.com")
