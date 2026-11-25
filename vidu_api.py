#!/usr/bin/env python3
"""Minimal Vidu API client for the official ent/v2 surface.

Official docs: https://platform.vidu.cn/docs
Base URL is https://api.vidu.cn (NOT the service.vidu.cn surface used by
third-party CLI tools). Auth header: Authorization: Token <your api key>.

Set VIDU_TOKEN to your API key (with or without the "Token " prefix).

Usage:
  python3 vidu_api.py tasks
  python3 vidu_api.py img2video <public_image_url> <prompt>
  python3 vidu_api.py creations <task_id>

Note: the image URL must be downloadable by Vidu's servers. Some file
sharing links return 403 to non-browser fetchers and the task then dies
with a vague InternalServiceFailure. Verify first with:
  curl -s -o /dev/null -w "%{http_code} %{content_type}\n" <image_url>
"""
import json, os, sys, urllib.request, urllib.error

BASE = "https://api.vidu.cn"

def token_header():
    raw = os.environ.get("VIDU_TOKEN", "").strip()
    if not raw:
        sys.exit("VIDU_TOKEN is not set")
    return raw if raw.startswith("Token ") else f"Token {raw}"

def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", token_header())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "tasks":
        print(json.dumps(call("GET", "/ent/v2/tasks"), ensure_ascii=False)[:3000])
    elif cmd == "creations" and len(sys.argv) > 2:
        print(json.dumps(call("GET", f"/ent/v2/tasks/{sys.argv[2]}/creations"), ensure_ascii=False)[:3000])
    elif cmd == "img2video" and len(sys.argv) > 3:
        body = {
            "model": "viduq4-preview",
            "images": [sys.argv[2]],
            "prompt": sys.argv[3],
            "duration": 5,
            "resolution": "720p",
            "audio": False,
            "watermark": False,
        }
        print(json.dumps(call("POST", "/ent/v2/img2video", body), ensure_ascii=False)[:3000])
    else:
        sys.exit(__doc__)
