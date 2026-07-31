from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

PROVIDERS = {"OPENAI", "GOOGLE", "OPENROUTER", "OLLAMA"}


def parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise RuntimeError("AI provider không trả JSON object")
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError as error:
            raise RuntimeError("AI provider trả JSON không hợp lệ") from error


def provider_config() -> tuple[str, str]:
    provider = os.getenv("AI_PROVIDER", "GOOGLE").upper()
    if provider not in PROVIDERS:
        raise ValueError(f"AI_PROVIDER phải là một trong: {', '.join(sorted(PROVIDERS))}")
    model = os.getenv("AI_MODEL") or (os.getenv("GEMINI_MODEL", "") if provider == "GOOGLE" else "")
    if not model:
        raise ValueError("AI_MODEL chưa được cấu hình")
    return provider, model


def _post_json(url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    timeout = min(max(int(os.getenv("AI_TIMEOUT", "90")), 1), 300)
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            try:
                return json.load(response)
            except UnicodeDecodeError as error:
                raise RuntimeError("AI provider không trả UTF-8 hợp lệ") from error
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"AI provider HTTP {error.code}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError("Không gọi được AI provider") from error


def generate_json(prompt: str, schema: dict[str, Any], system_prompt: str = "Return only JSON matching the supplied schema.") -> tuple[dict[str, Any], str, str]:
    provider, model = provider_config()
    max_tokens = min(max(int(os.getenv("AI_MAX_TOKENS", "1800")), 256), 8000)
    try:
        if provider == "GOOGLE":
            key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not key:
                raise ValueError("GOOGLE_API_KEY chưa được cấu hình")
            payload = _post_json(
                f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model, safe='._-')}:generateContent",
                {
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json", "responseSchema": schema, "maxOutputTokens": max_tokens},
                },
                {"x-goog-api-key": key},
            )
            text = payload["candidates"][0]["content"]["parts"][0]["text"]
        elif provider == "OLLAMA":
            payload = _post_json(
                f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')}/api/chat",
                {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "format": schema, "stream": False, "options": {"num_predict": max_tokens, "temperature": 0.2}},
                {},
            )
            text = payload["message"]["content"]
        else:
            key_name = f"{provider}_API_KEY"
            key = os.getenv(key_name)
            if not key:
                raise ValueError(f"{key_name} chưa được cấu hình")
            default_url = "https://api.openai.com/v1" if provider == "OPENAI" else "https://openrouter.ai/api/v1"
            base_url = os.getenv(f"{provider}_BASE_URL", default_url).rstrip("/")
            payload = _post_json(
                f"{base_url}/chat/completions",
                {
                    "model": model,
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "stream": False,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {"name": "labguard_requirements", "strict": True, "schema": schema},
                    },
                },
                {"Authorization": f"Bearer {key}"},
            )
            text = payload["choices"][0]["message"]["content"]
        return parse_json(text), provider, model
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("AI provider trả dữ liệu không hợp lệ") from error
