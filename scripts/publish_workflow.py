#!/usr/bin/env python3
"""Durable publish/resume workflow for Ken AI Daily."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"
LINKEDIN_PATH = ROOT / "linkedin-post.txt"
STATE_PATH = ROOT / ".publish-state.json"
SITE_URL = "https://kenchankh97.github.io/ai-daily/"
REQUIRED_LINKEDIN_MARKERS = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "Why it matters:",
    "Signal to watch:",
    "Question for the week:",
    "Today's focus:",
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class WorkflowError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass
class IssueFiles:
    date_id: str
    date_iso: str
    summary_png: Path
    top_news_png: Path


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_cmd(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def issue_files(date_id: str) -> IssueFiles:
    issue_date = datetime.strptime(date_id, "%Y%m%d").date()
    return IssueFiles(
        date_id=date_id,
        date_iso=issue_date.isoformat(),
        summary_png=ROOT / f"ai-daily-{date_id}.png",
        top_news_png=ROOT / f"ai-daily-{date_id}-top-news.png",
    )


def validate_local(files: IssueFiles) -> dict[str, Any]:
    errors: list[str] = []
    if not INDEX_PATH.exists():
        return {"ok": False, "errors": ["missing index.html"]}
    if not LINKEDIN_PATH.exists():
        return {"ok": False, "errors": [f"missing {LINKEDIN_PATH.name}"]}

    content = INDEX_PATH.read_text(encoding="utf-8")
    linkedin = LINKEDIN_PATH.read_text(encoding="utf-8")

    marker = f'id="post-visual-{files.date_id}"'
    if marker not in content:
        errors.append("missing issue marker in index.html")
    if files.summary_png.name not in content:
        errors.append("missing summary png reference in index.html")
    if ".post-visual img" not in content or "aspect-ratio" not in content:
        errors.append("missing .post-visual img aspect-ratio guard")
    if files.top_news_png.name == files.summary_png.name:
        errors.append("top-news image name matches summary image")

    for path in [files.summary_png, files.top_news_png]:
        if not path.exists():
            errors.append(f"missing image: {path.name}")
            continue
        with Image.open(path) as img:
            if img.size != (2400, 1350):
                errors.append(f"bad image size for {path.name}: {img.size}")

    for token in REQUIRED_LINKEDIN_MARKERS:
        if token not in linkedin:
            errors.append(f"missing linkedin marker: {token}")
    if "�" in linkedin or "�" in content:
        errors.append("replacement character found in content")

    return {
        "ok": not errors,
        "errors": errors,
        "marker": marker,
        "summary_png": files.summary_png.name,
        "top_news_png": files.top_news_png.name,
        "summary_png_bytes": files.summary_png.stat().st_size if files.summary_png.exists() else 0,
        "top_news_png_bytes": files.top_news_png.stat().st_size if files.top_news_png.exists() else 0,
    }


def git_status_lines() -> list[str]:
    result = run_git("status", "--short", "--untracked-files=all")
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_preflight() -> dict[str, Any]:
    lock_present = (ROOT / ".git" / "index.lock").exists()
    probe = ROOT / ".git" / "codex-write-test.tmp"
    write_ok = False
    write_error = ""
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        write_ok = True
    except OSError as exc:
        write_error = str(exc)

    details = {
        "index_lock_present": lock_present,
        "git_write_ok": write_ok,
        "git_write_error": write_error,
        "git_status": git_status_lines(),
    }
    if write_ok:
        return details

    identity = run_cmd("whoami").stdout.strip()
    acl = run_cmd("icacls", str(ROOT / ".git")).stdout.strip()
    details["whoami"] = identity
    details["icacls_git"] = acl
    if not lock_present and "denied" in write_error.lower():
        raise WorkflowError(
            "GIT_ACL_DENY_NO_LOCK",
            "Git preflight failed: .git is not writable and no index.lock exists.",
            details=details,
        )
    raise WorkflowError("GIT_PREFLIGHT_FAILED", "Git preflight failed.", details=details)


def commit_if_needed(date_iso: str, dry_run: bool) -> tuple[str, list[str]]:
    status_lines = git_status_lines()
    if dry_run:
        head = run_git("rev-parse", "--short", "HEAD").stdout.strip()
        return head, status_lines
    if status_lines:
        run_git("add", "-A")
        run_git("commit", "-m", f"Daily AI brief - {date_iso}")
    head = run_git("rev-parse", "--short", "HEAD").stdout.strip()
    return head, status_lines


def push_if_needed(dry_run: bool) -> str:
    if dry_run:
        return "dry-run"
    result = run_git("push", "origin", "main")
    return (result.stdout + result.stderr).strip()


def verify_pages(files: IssueFiles, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"verified": False, "mode": "dry-run", "url": SITE_URL}

    last_error = ""
    for attempt in range(1, 21):
        url = f"{SITE_URL}?v={files.date_id}-{int(time.time())}"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read().decode("utf-8", errors="replace")
                if f"post-visual-{files.date_id}" in content and files.summary_png.name in content:
                    return {
                        "verified": True,
                        "attempt": attempt,
                        "url": url,
                    }
                last_error = f"stale content on attempt {attempt}"
        except urllib.error.URLError as exc:
            last_error = f"attempt {attempt}: {exc}"
        time.sleep(6)
    raise WorkflowError(
        "PAGES_VERIFICATION_FAILED",
        "GitHub Pages did not show today's marker and PNG reference in time.",
        details={"last_error": last_error, "site_url": SITE_URL},
    )


def publish_linkedin(files: IssueFiles, title: str, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"share_urn": "dry-run", "published": False}
    result = run_cmd(
        sys.executable,
        str(ROOT / "scripts" / "linkedin_post_ugc.py"),
        "--text-file",
        str(LINKEDIN_PATH),
        "--image",
        str(files.top_news_png),
        "--title",
        title,
    )
    payload = json.loads(result.stdout)
    share_urn = payload["created"]["id"]
    return {"share_urn": share_urn, "published": True, "api_result": payload}


def validate_linkedin(share_urn: str, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"validated": False, "mode": "dry-run", "share_urn": share_urn}
    url = f"https://www.linkedin.com/feed/update/{share_urn}/"
    with urllib.request.urlopen(url, timeout=30) as response:
        content = response.read().decode("utf-8", errors="replace")
        checks = {
            "AI News Daily Brief": "AI News Daily Brief" in content,
            "Ken AI Daily": "Ken AI Daily" in content,
            "Today's focus": "Today's focus" in content,
            "Why it matters": "Why it matters" in content,
            "Signal to watch": "Signal to watch" in content,
            "Question for the week": "Question for the week" in content,
            "Full digest": "Full digest" in content,
            "attached_image_ref": ("dms.licdn.com" in content) or ("image" in content.lower()),
        }
    return {
        "validated": all(checks.values()),
        "url": url,
        "status_code": 200,
        "checks": checks,
    }


def bootstrap_state(files: IssueFiles, title: str) -> dict[str, Any]:
    state = load_state()
    if state.get("issue_date") != files.date_id:
        state = {}
    state["issue_date"] = files.date_id
    state["title"] = title
    state["artifacts"] = {
        "summary_png": files.summary_png.name,
        "top_news_png": files.top_news_png.name,
        "linkedin_text": LINKEDIN_PATH.name,
    }
    state.setdefault("status", "created")
    return state


def run_workflow(date_id: str, title: str, dry_run: bool) -> dict[str, Any]:
    files = issue_files(date_id)
    state = bootstrap_state(files, title)
    state["attempt_started_at"] = now_iso()

    local = validate_local(files)
    state["local_validation"] = local
    if not local["ok"]:
        state["status"] = "blocked"
        state["blocker"] = {"code": "NOT_PREPARED", "message": "Local artifacts are not ready.", "details": local}
        save_state(state)
        raise WorkflowError("NOT_PREPARED", "Local artifacts are not ready.", details=local)

    try:
        preflight = git_preflight()
        state["git_preflight"] = preflight
        commit_hash, dirty_before = commit_if_needed(files.date_iso, dry_run)
        state["git"] = {
            "commit_hash": commit_hash,
            "dirty_before_commit": dirty_before,
            "push_result": push_if_needed(dry_run),
        }
        state["pages"] = verify_pages(files, dry_run)
        share_urn = state.get("linkedin", {}).get("share_urn")
        if share_urn == "dry-run":
            share_urn = ""
        if not share_urn:
            linkedin = publish_linkedin(files, title, dry_run)
            state["linkedin"] = linkedin
            share_urn = linkedin["share_urn"]
        validation = validate_linkedin(share_urn, dry_run)
        state.setdefault("linkedin", {})["validation"] = validation
        state["status"] = "completed" if not dry_run else "dry-run"
        state.pop("blocker", None)
        save_state(state)
        return state
    except WorkflowError as exc:
        state["status"] = "blocked"
        state["blocker"] = {"code": exc.code, "message": str(exc), "details": exc.details}
        save_state(state)
        raise
    except subprocess.CalledProcessError as exc:
        details = {
            "cmd": exc.cmd,
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }
        state["status"] = "blocked"
        state["blocker"] = {"code": "COMMAND_FAILED", "message": str(exc), "details": details}
        save_state(state)
        raise WorkflowError("COMMAND_FAILED", "A publish command failed.", details=details) from exc
    except urllib.error.HTTPError as exc:
        details = {"url": exc.url, "status": exc.code, "body": exc.read().decode("utf-8", errors="replace")}
        code = "LINKEDIN_TOKEN_EXPIRED" if exc.code in (401, 403) else "HTTP_ERROR"
        state["status"] = "blocked"
        state["blocker"] = {"code": code, "message": str(exc), "details": details}
        save_state(state)
        raise WorkflowError(code, "HTTP request failed during publish workflow.", details=details) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Issue date in YYYYMMDD format")
    parser.add_argument("--title", required=True, help="LinkedIn post title")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without push or LinkedIn publish")
    args = parser.parse_args()

    try:
        result = run_workflow(args.date, args.title, args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except WorkflowError as exc:
        payload = {
            "ok": False,
            "code": exc.code,
            "message": str(exc),
            "details": exc.details,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
