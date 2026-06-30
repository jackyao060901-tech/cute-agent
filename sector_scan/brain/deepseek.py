"""DeepSeek Chat 客户端(大脑侧).

只用标准库。temperature 默认 0 以求可复现。模型默认 deepseek-v4-pro(质量优先)。
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from .. import config

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"


class DeepSeekError(RuntimeError):
    pass


def chat(
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    timeout: int = 60,
    response_json: bool = False,
) -> str:
    body = {"model": model, "messages": messages, "temperature": temperature}
    if response_json:
        body["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.deepseek_api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise DeepSeekError(f"HTTP {e.code}: {e.read().decode('utf-8','replace')}") from e
    except urllib.error.URLError as e:
        raise DeepSeekError(f"网络失败: {e}") from e
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise DeepSeekError(f"返回结构异常: {payload}") from e
