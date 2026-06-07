#!/usr/bin/env python3
"""Publish a prepared Ken AI Daily issue from a fresh clone.

Use this when today's local artifacts are already prepared and validated, but the
working clone is not safe to commit from because it is dirty, stale, or blocked
by local `.git` ACL issues. This helper clones the remote repo into a clean
temporary directory, copies only the prepared daily artifacts, stages an explicit
allowlist, pushes, verifies GitHub Pages, publishes LinkedIn, and validates the
rendered post shape.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_LINKEDIN_MARKERS = [
    "1\ufe0f\u20e3",
    "2\ufe0f\u20e3",
    "3\ufe0f\u20e3",
    "4\ufe0f\u20e3",
    "5\ufe0f\u20e3",
    "6\ufe0f\u20e3",
    "Why it matters:",
    "Signal to watch:",
    "Question for the week:",
    "Today's focus:",
]

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)
STATE_PATH_NAME = ".publish-state.json"


@dataclass
class Config:
    date_id: str
    date_iso: str
    title: str
    source_root: Path
    checkout: Path
    repo_url: str
    branch: str
    pages_url: str
    linkedin_activity_url: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_env_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def repo_https_url() -> str:
    repo = os.environ.get("GITHUB_REPO", "kenchankh97/ai-daily")
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"https://x-access-token:{token}@github.com/{repo}.git"
    return f"https://github.com/{repo}.git"


def redact_arg(value: str) -> str:
    return re.sub(r"(https://x-access-token:)[^@]+(@github\.com/)", r"\1***\2", value)


def redact_args(args: list[str]) -> list[str]:
    return [redact_arg(arg) for arg in args]


def run_cmd(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            json.dumps(
                {
                    "cmd": redact_args(args),
                    "code": result.returncode,
                    "stdout": result.stdout[-4000:],
                    "stderr": result.stderr[-4000:],
                },
                ensure_ascii=False,
            )
        )
    return result


def run_cmd_retry(
    args: list[str],
    *,
    cwd: Path | None = None,
    attempts: int = 3,
    delay_seconds: int = 12,
) -> subprocess.CompletedProcess[str]:
    last_error: RuntimeError | None = None
    for attempt in range(1, attempts + 1):
        try:
            return run_cmd(args, cwd=cwd)
        except RuntimeError as exc:
            last_error = exc
            if attempt == attempts:
                raise
            time.sleep(delay_seconds)
    if last_error is not None:
        raise last_error
    raise RuntimeError(json.dumps({"cmd": redact_args(args), "error": "unknown failure"}, ensure_ascii=False))


def fetch_text(url: str, *, user_agent: str = DEFAULT_USER_AGENT, timeout: int = 30) -> str:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", user_agent)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def issue_files(config: Config) -> list[str]:
    return [
        "index.html",
        f"ai-daily-{config.date_id}.png",
        f"ai-daily-{config.date_id}-top-news.png",
        "linkedin-post.txt",
    ]


def state_path(config: Config) -> Path:
    return config.source_root / STATE_PATH_NAME


def bootstrap_state(config: Config) -> dict[str, Any]:
    path = state_path(config)
    state = load_state(path)
    if state.get("issue_date") != config.date_id or state.get("resume_mode") != "fresh-clone-selective-stage":
        state = {}
    state["issue_date"] = config.date_id
    state["title"] = config.title
    state["resume_mode"] = "fresh-clone-selective-stage"
    state["artifacts"] = {
        "summary_png": f"ai-daily-{config.date_id}.png",
        "top_news_png": f"ai-daily-{config.date_id}-top-news.png",
        "linkedin_text": "linkedin-post.txt",
    }
    state.setdefault("status", "created")
    return state


def validate_prepared_source(config: Config) -> dict[str, Any]:
    errors: list[str] = []
    source = config.source_root
    index = source / "index.html"
    linkedin = source / "linkedin-post.txt"
    summary = source / f"ai-daily-{config.date_id}.png"
    top_news = source / f"ai-daily-{config.date_id}-top-news.png"

    if not index.exists():
        errors.append("missing source index.html")
    if not linkedin.exists():
        errors.append("missing source linkedin-post.txt")
    if index.exists():
        content = index.read_text(encoding="utf-8")
        if f"post-visual-{config.date_id}" not in content:
            errors.append("source index.html missing today's marker")
        if summary.name not in content:
            errors.append("source index.html missing summary PNG reference")
        if ".post-visual img" not in content or "aspect-ratio" not in content:
            errors.append("source index.html missing .post-visual img guard")
    if linkedin.exists():
        text = linkedin.read_text(encoding="utf-8-sig")
        for marker in REQUIRED_LINKEDIN_MARKERS:
            if marker not in text:
                errors.append(f"source linkedin-post.txt missing marker: {marker}")
    for image in [summary, top_news]:
        if not image.exists():
            errors.append(f"missing source image: {image.name}")
    return {"ok": not errors, "errors": errors}


def clone_fresh_checkout(config: Config) -> None:
    if config.checkout.exists():
        shutil.rmtree(config.checkout)
    config.checkout.parent.mkdir(parents=True, exist_ok=True)
    run_cmd_retry(["git", "clone", "--depth", "1", "--branch", config.branch, config.repo_url, str(config.checkout)], attempts=4, delay_seconds=15)
    run_cmd(["git", "config", "user.name", os.environ.get("GIT_AUTHOR_NAME", "Ken AI Daily Bot")], cwd=config.checkout)
    run_cmd(["git", "config", "user.email", os.environ.get("GIT_AUTHOR_EMAIL", "ken-ai-daily-bot@example.com")], cwd=config.checkout)


def copy_prepared_files(config: Config) -> None:
    for name in issue_files(config):
        shutil.copy2(config.source_root / name, config.checkout / name)
    env_path = config.checkout / ".env"
    lines = []
    for key, value in os.environ.items():
        if key.startswith(("LINKEDIN_", "GITHUB_", "DEEPSEEK_", "BRAVE_", "BING_", "TAVILY_")):
            lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def commit_and_push(config: Config) -> dict[str, Any]:
    status_before = run_cmd(["git", "status", "--short", "--untracked-files=all"], cwd=config.checkout).stdout.splitlines()
    allowed = [name for name in issue_files(config) if name != "linkedin-post.txt"]
    run_cmd(["git", "add", "--", *allowed], cwd=config.checkout)
    staged = run_cmd(["git", "diff", "--cached", "--name-only"], cwd=config.checkout).stdout.splitlines()
    unexpected = sorted(set(staged) - set(allowed))
    if unexpected:
        raise RuntimeError(json.dumps({"unexpected_staged_files": unexpected}, ensure_ascii=False))
    if staged:
        run_cmd(["git", "commit", "-m", f"Daily AI brief - {config.date_iso}"], cwd=config.checkout)
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"], cwd=config.checkout).stdout.strip()
    push = run_cmd_retry(["git", "push", "origin", config.branch], cwd=config.checkout, attempts=4, delay_seconds=15)
    return {
        "commit_hash": head,
        "dirty_before_commit": status_before,
        "staged": staged,
        "push_result": (push.stdout + push.stderr).strip(),
    }


def verify_pages(config: Config) -> dict[str, Any]:
    last_error = ""
    summary_name = f"ai-daily-{config.date_id}.png"
    for attempt in range(1, 21):
        url = f"{config.pages_url.rstrip('/')}?v={config.date_id}-{int(time.time())}"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read().decode("utf-8", errors="replace")
            if f"post-visual-{config.date_id}" in content and summary_name in content:
                return {"verified": True, "attempt": attempt, "url": url}
            last_error = f"stale content on attempt {attempt}"
        except urllib.error.URLError as exc:
            last_error = str(exc)
        time.sleep(6)
    raise RuntimeError(json.dumps({"pages_verification_failed": True, "last_error": last_error}, ensure_ascii=False))


def publish_linkedin(config: Config) -> dict[str, Any]:
    result = run_cmd(
        [
            sys.executable,
            str(config.checkout / "scripts" / "linkedin_post_ugc.py"),
            "--text-file",
            str(config.checkout / "linkedin-post.txt"),
            "--image",
            str(config.checkout / f"ai-daily-{config.date_id}-top-news.png"),
            "--title",
            config.title,
        ],
        cwd=config.checkout,
    )
    payload = json.loads(result.stdout)
    return {"share_urn": payload["created"]["id"], "published": True, "api_result": payload}


def validate_permalink(url: str) -> dict[str, Any]:
    content = fetch_text(url)
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
    return {"validated": all(checks.values()), "url": url, "checks": checks, "method": "permalink"}


def validate_public_activity(config: Config) -> dict[str, Any]:
    text = (config.source_root / "linkedin-post.txt").read_text(encoding="utf-8-sig")
    first_story_line = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("1️⃣"):
            first_story_line = stripped
            break
    content = fetch_text(config.linkedin_activity_url)
    checks = {
        "AI News Daily Brief": "AI News Daily Brief" in content,
        config.title: config.title in content,
        "Why it matters": "Why it matters" in content,
        "Signal to watch": "Signal to watch" in content,
        "Question for the week": "Question for the week" in content,
    }
    if first_story_line:
        checks["top_story_line"] = first_story_line in content
    return {
        "validated": all(checks.values()),
        "url": config.linkedin_activity_url,
        "checks": checks,
        "method": "public-activity-page-fallback",
        "caveat": "Direct LinkedIn permalink validation was unavailable; used public activity page fallback.",
    }


def validate_linkedin(share_urn: str, config: Config) -> dict[str, Any]:
    url = f"https://www.linkedin.com/feed/update/{share_urn}/"
    last_error = ""
    last_result: dict[str, Any] | None = None
    for attempt in range(1, 7):
        try:
            result = validate_permalink(url)
            result["attempt"] = attempt
            if result.get("validated"):
                return result
            last_result = result
            last_error = "permalink returned before expected post text was visible"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code not in (404, 999):
                raise
        except urllib.error.URLError as exc:
            last_error = str(exc)
        if attempt < 6:
            time.sleep(10)
    fallback = validate_public_activity(config)
    fallback["permalink_url"] = url
    fallback["permalink_error"] = last_error or "unavailable"
    if last_result is not None:
        fallback["last_permalink_validation"] = last_result
    return fallback


def result_payload(state: dict[str, Any], ok: bool, **extra: Any) -> dict[str, Any]:
    payload = {"ok": ok}
    payload.update(extra)
    payload.update(state)
    return payload


def build_config(args: argparse.Namespace) -> Config:
    if args.env_file:
        load_env_file(Path(args.env_file))
    date_id = args.date
    date_iso = datetime.strptime(date_id, "%Y%m%d").date().isoformat()
    title = args.title or f"Ken AI Daily {date_iso}"
    checkout = Path(args.checkout or (Path.home() / ".ken-ai-daily" / "work" / f"manual-publish-{date_id}"))
    return Config(
        date_id=date_id,
        date_iso=date_iso,
        title=title,
        source_root=Path(args.source_root).resolve(),
        checkout=checkout.resolve(),
        repo_url=repo_https_url(),
        branch=os.environ.get("GITHUB_BRANCH", "main"),
        pages_url=os.environ.get("PAGES_URL", "https://kenchankh97.github.io/ai-daily/"),
        linkedin_activity_url=os.environ.get(
            "LINKEDIN_PUBLIC_ACTIVITY_URL",
            "https://www.linkedin.com/in/ken-chan-1b247720/recent-activity/all/",
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Issue date in YYYYMMDD format")
    parser.add_argument("--source-root", required=True, help="Path containing prepared index/image/post artifacts")
    parser.add_argument("--env-file", help="Optional env file containing GitHub and LinkedIn credentials")
    parser.add_argument("--title", help="LinkedIn post title")
    parser.add_argument("--checkout", help="Optional fresh checkout path")
    args = parser.parse_args()

    config = build_config(args)
    state_file = state_path(config)
    state = bootstrap_state(config)
    state["attempt_started_at"] = now_iso()

    source_validation = validate_prepared_source(config)
    state["source_validation"] = source_validation
    if not source_validation["ok"]:
        state["status"] = "blocked"
        state["blocker"] = {"code": "SOURCE_VALIDATION_FAILED", "details": source_validation}
        save_state(state_file, state)
        print(json.dumps(result_payload(state, False, error="SOURCE_VALIDATION_FAILED"), ensure_ascii=False, indent=2))
        raise SystemExit(1)

    if state.get("status") == "completed":
        print(json.dumps(result_payload(state, True), ensure_ascii=False, indent=2))
        return

    try:
        git_result = state.get("git")
        if not git_result:
            clone_fresh_checkout(config)
            copy_prepared_files(config)
            git_result = commit_and_push(config)
            state["git"] = git_result
            state["status"] = "pushed"
            state["blocker"] = None
            save_state(state_file, state)

        pages = state.get("pages")
        if not (isinstance(pages, dict) and pages.get("verified")):
            pages = verify_pages(config)
            state["pages"] = pages
            state["status"] = "pages_verified"
            state["blocker"] = None
            save_state(state_file, state)

        linkedin = state.get("linkedin")
        if not (isinstance(linkedin, dict) and linkedin.get("share_urn")):
            linkedin = publish_linkedin(config)
            state["linkedin"] = linkedin
            state["status"] = "linkedin_published"
            state["blocker"] = None
            save_state(state_file, state)

        validation = state.get("linkedin", {}).get("validation")
        if not (isinstance(validation, dict) and validation.get("validated")):
            validation = validate_linkedin(state["linkedin"]["share_urn"], config)
            state.setdefault("linkedin", {})["validation"] = validation
            save_state(state_file, state)

        if state["linkedin"]["validation"].get("validated"):
            state["status"] = "completed"
            state["completed_at"] = now_iso()
            state["blocker"] = None
            save_state(state_file, state)
            print(json.dumps(result_payload(state, True, commit_hash=state["git"]["commit_hash"]), ensure_ascii=False, indent=2))
            return

        state["status"] = "linkedin_published"
        state["blocker"] = {
            "code": "LINKEDIN_VALIDATION_PENDING",
            "details": state["linkedin"]["validation"],
        }
        save_state(state_file, state)
        print(json.dumps(result_payload(state, False, error="LINKEDIN_VALIDATION_PENDING"), ensure_ascii=False, indent=2))
        raise SystemExit(1)
    except Exception as exc:
        details: dict[str, Any]
        try:
            details = json.loads(str(exc))
        except json.JSONDecodeError:
            details = {"message": str(exc)}
        state["status"] = state.get("status", "blocked")
        if state["status"] == "created":
            state["status"] = "blocked"
        state["blocker"] = {
            "code": "PUBLISH_FAILED",
            "details": details,
        }
        save_state(state_file, state)
        print(json.dumps(result_payload(state, False, error="PUBLISH_FAILED"), ensure_ascii=False, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
