#!/usr/bin/env python3
"""Publish a LinkedIn UGC image post with full commentary text."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()


def api_json(url: str, *, method: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Restli-Protocol-Version", "2.0.0")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = response.read().decode("utf-8")
            if payload:
                return json.loads(payload)
            return {"status": response.status, "headers": dict(response.headers)}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn API error {exc.code} for {url}: {detail}") from exc


def upload_binary(upload_url: str, image_path: Path, token: str) -> None:
    req = urllib.request.Request(upload_url, data=image_path.read_bytes(), method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", mimetypes.guess_type(image_path.name)[0] or "application/octet-stream")
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            if response.status not in (200, 201, 202):
                raise RuntimeError(f"Unexpected upload status: {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn upload error {exc.code}: {detail}") from exc


def delete_post(urn: str, token: str) -> dict:
    url = "https://api.linkedin.com/rest/posts/" + urllib.parse.quote(urn, safe="")
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Linkedin-Version", os.environ.get("LINKEDIN_API_VERSION", "202604"))
    req.add_header("X-Restli-Protocol-Version", "2.0.0")
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return {"deleted": True, "status": response.status}
    except urllib.error.HTTPError as exc:
        return {"deleted": False, "status": exc.code, "body": exc.read().decode("utf-8", errors="replace")}


def publish(text: str, image_path: Path, title: str) -> None:
    load_env(ROOT / ".env")
    token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    author = os.environ["LINKEDIN_AUTHOR_URN"]

    register = api_json(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        method="POST",
        token=token,
        body={
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        },
    )
    value = register["value"]
    asset = value["asset"]
    upload_url = value["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    upload_binary(upload_url, image_path, token)

    post = api_json(
        "https://api.linkedin.com/v2/ugcPosts",
        method="POST",
        token=token,
        body={
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": "Ken AI Daily infographic"},
                            "media": asset,
                            "title": {"text": title},
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        },
    )
    print(json.dumps({"created": post}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--delete-after-success")
    args = parser.parse_args()
    text = args.text_file.read_text(encoding="utf-8-sig").strip()
    publish(text, args.image.resolve(), args.title)
    if args.delete_after_success:
        load_env(ROOT / ".env")
        print(json.dumps(delete_post(args.delete_after_success, os.environ["LINKEDIN_ACCESS_TOKEN"]), indent=2))


if __name__ == "__main__":
    main()
