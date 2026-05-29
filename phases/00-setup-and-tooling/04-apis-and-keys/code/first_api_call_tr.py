# Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/04-apis-and-keys/code/first_api_call.py
# Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

import os
import json
import urllib.request


def call_with_sdk():
    try:
        import anthropic
    except ImportError:
        print("SDK'ı yükleyin: pip install anthropic")
        return

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": "Sinir ağı tek cümlede nedir?"}]
    )
    print(f"SDK yanıtı: {response.content[0].text}")
    print(f"Kullanılan token'lar: {response.usage.input_tokens} giriş, {response.usage.output_tokens} çıkış")


def call_raw_http():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Önce ANTHROPIC_API_KEY ortam değişkenini ayarlayın")
        return

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": "Sinir ağı tek cümlede nedir?"}],
    }).encode()

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"Ham HTTP yanıtı: {result['content'][0]['text']}")
        print(f"Kullanılan token'lar: {result['usage']['input_tokens']} giriş, {result['usage']['output_tokens']} çıkış")


if __name__ == "__main__":
    print("=== API Çağrıları ===\n")
    print("1. SDK kullanarak:")
    call_with_sdk()
    print("\n2. Ham HTTP kullanarak:")
    call_raw_http()
