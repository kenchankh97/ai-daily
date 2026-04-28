#!/usr/bin/env python3
"""Publish a LinkedIn member post with one image."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request_json(url: str, *, method: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Linkedin-Version", os.environ.get("LINKEDIN_API_VERSION", "202604"))
    req.add_header("X-Restli-Protocol-Version", "2.0.0")
    if data is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = response.read().decode("utf-8")
            if not payload:
                return {"status": response.status, "headers": dict(response.headers)}
            return json.loads(payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn API error {exc.code} for {url}: {detail}") from exc


def upload_image(upload_url: str, image_path: Path, token: str) -> None:
    mime_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    req = urllib.request.Request(upload_url, data=image_path.read_bytes(), method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", mime_type)

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            if response.status not in (200, 201, 202):
                raise RuntimeError(f"Unexpected image upload status: {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn image upload error {exc.code}: {detail}") from exc


def publish(text: str, image_path: Path, title: str, dry_run: bool) -> None:
    load_env(ROOT / ".env")
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    author = os.environ.get("LINKEDIN_AUTHOR_URN")
    if not token or not author:
        raise SystemExit("Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN in .env")
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    if dry_run:
        print(json.dumps({"author": author, "image": str(image_path), "text": text}, indent=2, ensure_ascii=False))
        return

    init = request_json(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        method="POST",
        token=token,
        body={"initializeUploadRequest": {"owner": author}},
    )
    value = init.get("value") or {}
    upload_url = value.get("uploadUrl")
    image_urn = value.get("image")
    if not upload_url or not image_urn:
        raise RuntimeError(f"Unexpected initializeUpload response: {json.dumps(init, indent=2)}")

    upload_image(upload_url, image_path, token)

    post_body = {
        "author": author,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": title,
                "id": image_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    result = request_json("https://api.linkedin.com/rest/posts", method="POST", token=token, body=post_body)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--title", default="Ken AI Daily")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = args.text_file.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise SystemExit("Post text is empty")
    publish(text, args.image.resolve(), args.title, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise
