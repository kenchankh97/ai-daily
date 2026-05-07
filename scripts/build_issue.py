#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import textwrap
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"
LINKEDIN_PATH = ROOT / "linkedin-post.txt"
DATE_ID = "20260507"
ISSUE_DATE = datetime.strptime(DATE_ID, "%Y%m%d").date()
PREVIOUS_DATE_ID = (ISSUE_DATE - timedelta(days=1)).strftime("%Y%m%d")
DISPLAY_DATE = f"{ISSUE_DATE.strftime('%B')} {ISSUE_DATE.day}, {ISSUE_DATE.year}"
MONTH_DAY = f"{ISSUE_DATE.strftime('%B')} {ISSUE_DATE.day}"
DAY_NAME = ISSUE_DATE.strftime("%A")
SUMMARY_PNG = ROOT / f"ai-daily-{DATE_ID}.png"
TOP_NEWS_PNG = ROOT / f"ai-daily-{DATE_ID}-top-news.png"

FONT_CJK = Path("C:/Windows/Fonts/msjh.ttc")
FONT_LATIN_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
FONT_LATIN = Path("C:/Windows/Fonts/segoeui.ttf")


STORIES = [
    {
        "rank": 1,
        "category": "AI Regulation",
        "color": "#f59e0b",
        "emoji": "\U0001f6e1\ufe0f",
        "source": "NIST / CAISI",
        "source_label": "NIST \u2192",
        "source_url": "https://www.nist.gov/news-events/news/2026/05/caisi-signs-agreements-regarding-frontier-ai-national-security-testing",
        "headline_en": "U.S. CAISI Expands Frontier AI Pre-Deployment Testing With Google DeepMind, Microsoft and xAI",
        "headline_zh": "\u7f8e\u570b CAISI \u8207 Google DeepMind\u3001Microsoft\u3001xAI \u64f4\u5927\u524d\u6cbf AI \u767c\u5e03\u524d\u6e2c\u8a66",
        "body_en": "NIST said CAISI signed new agreements with Google DeepMind, Microsoft and xAI to run pre-deployment evaluations, targeted research and classified-environment testing on frontier models. CAISI said it has already completed more than 40 such evaluations, showing how government stress testing is moving directly into the release path for top labs.",
        "body_zh": "NIST \u8868\u793a\uff0cCAISI \u5df2\u8207 Google DeepMind\u3001Microsoft \u53ca xAI \u7c3d\u7f72\u65b0\u5354\u8b70\uff0c\u5c07\u5c0d\u524d\u6cbf\u6a21\u578b\u9032\u884c\u767c\u5e03\u524d\u8a55\u4f30\u3001\u91dd\u5c0d\u6027\u7814\u7a76\u8207\u6a5f\u5bc6\u74b0\u5883\u6e2c\u8a66\u3002CAISI \u4e26\u6307\u51fa\u81f3\u4eca\u5df2\u5b8c\u6210\u8d85\u904e 40 \u6b21\u6a21\u578b\u8a55\u4f30\uff0c\u986f\u793a\u653f\u5e9c\u58d3\u529b\u6e2c\u8a66\u6b63\u76f4\u63a5\u9032\u5165\u9802\u5c16 AI \u5be6\u9a57\u5ba4\u7684\u767c\u5e03\u6d41\u7a0b\u3002",
        "svg_title": "CAISI Expands Frontier AI Pre-Deployment Testing",
        "svg_source": "NIST / CAISI",
        "variant": "policy_gate",
        "top_label": "Top News \u00b7 #1 \u00b7 AI Regulation",
        "top_source": "Source: NIST / CAISI \u00b7 May 5, 2026",
        "top_bullets": [
            "New agreements cover Google DeepMind, Microsoft and xAI.",
            "CAISI says it has already completed more than 40 model evaluations.",
            "Testing spans pre-release, post-deployment and classified settings.",
        ],
        "top_nodes": [
            ("Labs", "frontier models"),
            ("CAISI", "40+ evals"),
            ("Deploy", "classified tests"),
        ],
    },
    {
        "rank": 2,
        "category": "AI Business",
        "color": "#06b6d4",
        "emoji": "\U0001f4b0",
        "source": "OpenAI",
        "source_label": "OpenAI \u2192",
        "source_url": "https://openai.com/index/new-ways-to-buy-chatgpt-ads/",
        "headline_en": "OpenAI Expands ChatGPT Ads With Self-Serve Buying and CPC Bidding",
        "headline_zh": "OpenAI \u64f4\u5927 ChatGPT \u5ee3\u544a\u5e73\u53f0\uff0c\u52a0\u5165\u81ea\u52a9\u6295\u653e\u8207 CPC \u7af6\u50f9",
        "body_en": "OpenAI said advertisers can now buy ChatGPT ads through partners or a beta self-serve Ads Manager in the U.S., with new cost-per-click bidding and expanded measurement tools. The move pushes ChatGPT further from an experimental traffic surface toward a scaled AI discovery and monetization channel.",
        "body_zh": "OpenAI \u8868\u793a\uff0c\u7f8e\u570b\u5ee3\u544a\u4e3b\u73fe\u53ef\u900f\u904e\u5408\u4f5c\u5925\u4f34\u6216\u6e2c\u8a66\u7248\u81ea\u52a9 Ads Manager \u76f4\u63a5\u8cfc\u8cb7 ChatGPT \u5ee3\u544a\uff0c\u4e26\u65b0\u589e\u6309\u9ede\u64ca\u4ed8\u8cbb\u8207\u66f4\u5b8c\u6574\u7684\u6210\u6548\u8861\u91cf\u5de5\u5177\u3002\u9019\u4ee3\u8868 ChatGPT \u6b63\u5f9e\u5be6\u9a57\u6027\u6d41\u91cf\u5165\u53e3\uff0c\u8f49\u5411\u53ef\u898f\u6a21\u5316\u7684 AI \u5206\u767c\u8207\u8b8a\u73fe\u6e20\u9053\u3002",
        "svg_title": "ChatGPT Ads Add Self-Serve Buying and CPC Bidding",
        "svg_source": "OpenAI",
        "variant": "ads_market",
    },
    {
        "rank": 3,
        "category": "AI Models",
        "color": "#ef4444",
        "emoji": "\U0001f916",
        "source": "OpenAI",
        "source_label": "OpenAI \u2192",
        "source_url": "https://openai.com/index/gpt-5-5-instant/",
        "headline_en": "OpenAI Makes GPT-5.5 Instant the New Default ChatGPT Model",
        "headline_zh": "OpenAI \u5c07 GPT-5.5 Instant \u5347\u7d1a\u70ba ChatGPT \u65b0\u9810\u8a2d\u6a21\u578b",
        "body_en": "OpenAI said GPT-5.5 Instant is now the default ChatGPT model for everyone, with clearer responses, stronger image and STEM performance, and better web-search judgment. In internal evaluations, it produced 52.5% fewer hallucinated claims than GPT-5.3 Instant on high-stakes prompts, turning a model update into a major distribution event.",
        "body_zh": "OpenAI \u8868\u793a GPT-5.5 Instant \u5df2\u6210\u70ba ChatGPT \u65b0\u7684\u9810\u8a2d\u6a21\u578b\uff0c\u56de\u7b54\u66f4\u6e05\u6670\uff0c\u5728\u5716\u50cf\u3001STEM \u8207\u7db2\u8def\u641c\u5c0b\u5224\u65b7\u4e0a\u8868\u73fe\u66f4\u5f37\u3002\u516c\u53f8\u6307\u51fa\uff0c\u5b83\u5728\u9ad8\u98a8\u96aa\u63d0\u793a\u4e0a\u6bd4 GPT-5.3 Instant \u6e1b\u5c11 52.5% \u7684\u5e7b\u89ba\u5f0f\u932f\u8aa4\u6558\u8ff0\uff0c\u8b93\u4e00\u6b21\u6a21\u578b\u66f4\u65b0\u76f4\u63a5\u8b8a\u6210\u6d88\u8cbb\u7aef\u5206\u767c\u4e8b\u4ef6\u3002",
        "svg_title": "GPT-5.5 Instant Becomes the New Default ChatGPT Model",
        "svg_source": "OpenAI",
        "variant": "model_upgrade",
    },
    {
        "rank": 4,
        "category": "Enterprise AI",
        "color": "#f97316",
        "emoji": "\U0001f3e6",
        "source": "Anthropic",
        "source_label": "Anthropic \u2192",
        "source_url": "https://www.anthropic.com/news/finance-agents",
        "headline_en": "Anthropic Launches 10 Finance Agent Templates and Microsoft 365 Add-Ins",
        "headline_zh": "Anthropic \u63a8\u51fa 10 \u6b3e\u91d1\u878d AI \u4ee3\u7406\u7bc4\u672c\uff0c\u4e26\u5ef6\u4f38\u81f3 Microsoft 365",
        "body_en": "Anthropic released ten ready-to-run agent templates for work such as pitchbooks, KYC screening and month-end close, while extending Claude into Excel, PowerPoint, Word and soon Outlook. The launch shows how enterprise AI is shifting from generic chat to packaged, governed workflows that fit directly into regulated desk work.",
        "body_zh": "Anthropic \u63a8\u51fa 10 \u6b3e\u53ef\u76f4\u63a5\u4e0a\u624b\u7684\u91d1\u878d AI \u4ee3\u7406\u7bc4\u672c\uff0c\u6db5\u84cb pitchbook\u3001KYC \u5be9\u67e5\u8207\u6708\u7d50\u6d41\u7a0b\uff0c\u540c\u6642\u4e5f\u5c07 Claude \u5ef6\u4f38\u5230 Excel\u3001PowerPoint\u3001Word \u8207\u5373\u5c07\u652f\u63f4\u7684 Outlook\u3002\u9019\u986f\u793a\u4f01\u696d AI \u6b63\u5f9e\u901a\u7528\u5c0d\u8a71\uff0c\u8f49\u5411\u53ef\u88ab\u6cbb\u7406\u3001\u53ef\u76f4\u63a5\u5d4c\u5165\u53d7\u76e3\u7ba1\u5de5\u4f5c\u6aaf\u7684\u6253\u5305\u6d41\u7a0b\u3002",
        "svg_title": "Anthropic Launches 10 Finance Agent Templates",
        "svg_source": "Anthropic",
        "variant": "finance_flow",
    },
    {
        "rank": 5,
        "category": "AI Developer Tools",
        "color": "#22c55e",
        "emoji": "\U0001f9f0",
        "source": "Google DeepMind",
        "source_label": "Google \u2192",
        "source_url": "https://blog.google/innovation-and-ai/technology/developers-tools/expanded-gemini-api-file-search-multimodal-rag/",
        "headline_en": "Google Makes Gemini File Search Multimodal With Metadata and Page Citations",
        "headline_zh": "Google \u8b93 Gemini File Search \u652f\u63f4\u591a\u6a21\u614b\u3001\u5f8c\u8a2d\u8cc7\u6599\u8207\u9801\u9762\u5f15\u7528",
        "body_en": "Google said Gemini API File Search now supports multimodal retrieval, custom metadata filtering and page-level citations for verifiable RAG. That matters because developers are no longer just querying text chunks; they are building grounded agent systems across mixed image and document corpora.",
        "body_zh": "Google \u8868\u793a\uff0cGemini API File Search \u73fe\u5df2\u652f\u63f4\u591a\u6a21\u614b\u6aa2\u7d22\u3001\u81ea\u8a02\u5f8c\u8a2d\u8cc7\u6599\u7be9\u9078\uff0c\u4ee5\u53ca\u9801\u9762\u7d1a\u5f15\u7528\uff0c\u53ef\u7528\u4f86\u5efa\u7acb\u53ef\u9a57\u8b49\u7684 RAG \u7cfb\u7d71\u3002\u9019\u4ee3\u8868\u958b\u767c\u8005\u5df2\u4e0d\u53ea\u662f\u67e5\u8a62\u6587\u5b57\u7247\u6bb5\uff0c\u800c\u662f\u5728\u5716\u50cf\u8207\u6587\u4ef6\u6df7\u5408\u8a9e\u6599\u4e0a\u5efa\u7acb\u6709\u4f9d\u64da\u7684 agent \u7cfb\u7d71\u3002",
        "svg_title": "Gemini File Search Goes Multimodal for Verifiable RAG",
        "svg_source": "Google DeepMind",
        "variant": "retrieval_grid",
    },
    {
        "rank": 6,
        "category": "AI Agents",
        "color": "#14b8a6",
        "emoji": "\U0001f9ed",
        "source": "NVIDIA / ServiceNow",
        "source_label": "NVIDIA \u2192",
        "source_url": "https://blogs.nvidia.com/blog/servicenow-autonomous-ai-agents-enterprises/",
        "headline_en": "NVIDIA and ServiceNow Unveil Governed Autonomous Agents for Enterprise Workflows",
        "headline_zh": "NVIDIA \u8207 ServiceNow \u63a8\u51fa\u53ef\u6cbb\u7406\u7684\u81ea\u4e3b AI \u4ee3\u7406\uff0c\u76f4\u63a5\u5207\u5165\u4f01\u696d\u5de5\u4f5c\u6d41",
        "body_en": "NVIDIA and ServiceNow said they are expanding their collaboration around governed autonomous agents, including Project Arc and the OpenShell secure runtime for sandboxed, policy-governed execution. The story matters because the enterprise agent race is shifting from demos toward controlled execution, auditability and runtime security.",
        "body_zh": "NVIDIA \u8207 ServiceNow \u8868\u793a\uff0c\u5c07\u570d\u7e5e\u53ef\u6cbb\u7406\u7684\u81ea\u4e3b AI \u4ee3\u7406\u64f4\u5927\u5408\u4f5c\uff0c\u5305\u62ec Project Arc \u8207 OpenShell \u9019\u500b\u7528\u65bc sandbox \u53ca\u653f\u7b56\u63a7\u5236\u7684\u5b89\u5168\u57f7\u884c\u74b0\u5883\u3002\u9019\u986f\u793a\u4f01\u696d agent \u7af6\u722d\u5df2\u5f9e demo \u9636\u6bb5\uff0c\u8f49\u5411\u53ef\u63a7\u57f7\u884c\u3001\u53ef\u7a3d\u6838\u6027\u8207 runtime \u5b89\u5168\u3002",
        "svg_title": "NVIDIA and ServiceNow Push Governed Autonomous Agents",
        "svg_source": "NVIDIA / ServiceNow",
        "variant": "agent_runtime",
    },
]


LEAD = {
    "kicker": f"The Cover Story \u00b7 {MONTH_DAY}",
    "headline_html": "AI is shifting from a <em>model race to a battle over distribution, release gates and governed execution.</em>",
    "deck_en": "From U.S. pre-deployment testing and ChatGPT ads monetization to OpenAI's new default model, Anthropic's finance agents, Google's verifiable RAG tooling and NVIDIA-ServiceNow runtime controls, today's AI market is organizing around who can ship, route and govern real work.",
    "deck_zh": "\u5f9e\u7f8e\u570b\u7684\u767c\u5e03\u524d\u6e2c\u8a66\u3001ChatGPT \u5ee3\u544a\u8b8a\u73fe\uff0c\u5230 OpenAI \u65b0\u9810\u8a2d\u6a21\u578b\u3001Anthropic \u91d1\u878d agent\u3001Google \u7684\u53ef\u9a57\u8b49 RAG \u5de5\u5177\uff0c\u4ee5\u53ca NVIDIA-ServiceNow \u7684 runtime \u63a7\u5236\uff0cAI \u5e02\u5834\u6b63\u5728\u91cd\u7d44\u6210\u300c\u8ab0\u80fd\u66f4\u597d\u5730\u767c\u5e03\u3001\u5206\u767c\u8207\u6cbb\u7406\u5be6\u969b\u5de5\u4f5c\u300d\u7684\u6230\u5834\u3002",
}

TICKER = [
    ("CAISI testing", "40+<span class=\"small\">model evals</span>"),
    ("ChatGPT ads", "CPC<span class=\"small\">+ self-serve beta</span>"),
    ("GPT-5.5 Instant", "52.5%<span class=\"small\">fewer hallucinations</span>"),
    ("Finance agents", "10<span class=\"small\">Anthropic templates</span>"),
]

LINKEDIN_HOOK = "AI is no longer just a benchmark race. The new contest is over who controls release gates, distribution, workflow entry points and governed execution."
LINKEDIN_FOCUS = "Today's six stories show AI becoming a full operating stack for institutions: governments want pre-release access, platforms want monetized distribution, labs are resetting default user experiences, and enterprises want agents embedded in the software they already trust."
LINKEDIN_WHY = "For leaders, the moat is widening beyond raw model quality. The next winners will combine stronger models with dependable routes to market, product surfaces users already inhabit, and governance layers that let AI do real work without losing control."
LINKEDIN_SIGNAL = "Watch more vendors bundle models with distribution, vertical workflows and policy-aware runtimes. The next phase of AI competition will be decided as much by execution channels as by frontier research."
LINKEDIN_QUESTION = "Over the next year, what will matter more: the best model, or the best control over where and how it gets used?"

SUMMARY_THEME_EN = "Distribution, governance and workflow control are becoming AI's new battleground."
SUMMARY_THEME_ZH = "\u5206\u767c\u3001\u6cbb\u7406\u8207\u5de5\u4f5c\u6d41\u63a7\u5236\uff0c\u6b63\u6210\u70ba AI \u65b0\u6230\u5834\u3002"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def wrap_by_width(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=text_font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def wrap_cjk(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if current and draw.textbbox((0, 0), candidate, font=text_font)[2] > max_width:
            lines.append(current)
            current = ch
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def draw_lines(
    draw: ImageDraw.ImageDraw,
    lines: Iterable[str],
    xy: tuple[int, int],
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    spacing: int,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=text_font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=text_font)
        y = bbox[3] + spacing
    return y


def svg_variant(story: dict) -> str:
    title_line = html.escape(textwrap.shorten(story["svg_title"], width=62, placeholder="..."))
    color = story["color"]
    category = html.escape(story["category"].upper())
    source = html.escape(story["svg_source"])
    rank = story["rank"]

    if story["variant"] == "policy_gate":
        center = f"""
<rect x="82" y="94" width="124" height="88" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="228" y="78" width="124" height="120" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="374" y="94" width="124" height="88" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M206 138 H228 M352 138 H374" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="144" y="144" font-size="17" fill="#f8fafc" text-anchor="middle">Labs</text>
<text x="290" y="132" font-size="17" fill="#f8fafc" text-anchor="middle">CAISI</text>
<text x="290" y="156" font-size="12" fill="#cbd5e1" text-anchor="middle">pre-release evals</text>
<text x="436" y="144" font-size="17" fill="#f8fafc" text-anchor="middle">Deploy</text>
"""
    elif story["variant"] == "model_upgrade":
        center = f"""
<rect x="88" y="92" width="166" height="104" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="322" y="92" width="166" height="104" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<text x="171" y="132" font-size="18" fill="#f8fafc" text-anchor="middle">GPT-5.3</text>
<text x="171" y="158" font-size="12" fill="#cbd5e1" text-anchor="middle">older default</text>
<text x="405" y="132" font-size="18" fill="#f8fafc" text-anchor="middle">GPT-5.5</text>
<text x="405" y="158" font-size="12" fill="#cbd5e1" text-anchor="middle">new default</text>
<path d="M254 144 H322" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="290" y="124" font-size="11" fill="#cbd5e1" text-anchor="middle">52.5% fewer hallucinations</text>
"""
    elif story["variant"] == "ads_market":
        center = f"""
<rect x="70" y="94" width="132" height="90" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="224" y="78" width="132" height="122" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="378" y="94" width="132" height="90" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M202 139 H224 M356 139 H378" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="136" y="130" font-size="15" fill="#f8fafc" text-anchor="middle">Brands</text>
<text x="136" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">partners</text>
<text x="290" y="128" font-size="15" fill="#f8fafc" text-anchor="middle">Ads Manager</text>
<text x="290" y="152" font-size="11" fill="#cbd5e1" text-anchor="middle">self-serve beta</text>
<text x="444" y="130" font-size="15" fill="#f8fafc" text-anchor="middle">ChatGPT</text>
<text x="444" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">CPC buying</text>
"""
    elif story["variant"] == "compute_pipeline":
        center = f"""
<rect x="84" y="104" width="122" height="70" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="228" y="86" width="122" height="106" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="372" y="104" width="122" height="70" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<path d="M206 139 H228 M350 139 H372" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="145" y="136" font-size="15" fill="#f8fafc" text-anchor="middle">Capital</text>
<text x="289" y="128" font-size="15" fill="#f8fafc" text-anchor="middle">Cloud + TPU</text>
<text x="289" y="151" font-size="11" fill="#cbd5e1" text-anchor="middle">5-year commitment</text>
<text x="433" y="136" font-size="15" fill="#f8fafc" text-anchor="middle">Capacity</text>
"""
    elif story["variant"] == "retrieval_grid":
        center = f"""
<rect x="96" y="88" width="120" height="72" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="232" y="88" width="120" height="72" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="368" y="88" width="120" height="72" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="164" y="184" width="120" height="50" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="300" y="184" width="120" height="50" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<path d="M216 124 H232 M352 124 H368 M224 184 L232 160 M360 184 L352 160 M284 209 H300" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
<text x="156" y="131" font-size="12" fill="#f8fafc" text-anchor="middle">Images</text>
<text x="292" y="131" font-size="12" fill="#f8fafc" text-anchor="middle">Metadata</text>
<text x="428" y="131" font-size="12" fill="#f8fafc" text-anchor="middle">Pages</text>
<text x="224" y="214" font-size="11" fill="#f8fafc" text-anchor="middle">grounding</text>
<text x="360" y="214" font-size="11" fill="#f8fafc" text-anchor="middle">citations</text>
"""
    elif story["variant"] == "agent_runtime":
        center = f"""
<circle cx="126" cy="138" r="40" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="220" y="96" width="146" height="82" rx="14" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="410" y="84" width="92" height="36" rx="10" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="410" y="128" width="92" height="36" rx="10" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="410" y="172" width="92" height="36" rx="10" fill="#111827" stroke="{color}" stroke-width="3"/>
<path d="M166 138 H220 M366 138 H410" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="126" y="145" font-size="15" fill="#f8fafc" text-anchor="middle">Arc</text>
<text x="293" y="128" font-size="16" fill="#f8fafc" text-anchor="middle">OpenShell</text>
<text x="293" y="151" font-size="12" fill="#cbd5e1" text-anchor="middle">secure runtime</text>
<text x="456" y="107" font-size="11" fill="#f8fafc" text-anchor="middle">sandbox</text>
<text x="456" y="151" font-size="11" fill="#f8fafc" text-anchor="middle">policy</text>
<text x="456" y="195" font-size="11" fill="#f8fafc" text-anchor="middle">audit</text>
"""
    else:
        center = f"""
<rect x="96" y="90" width="118" height="64" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="232" y="90" width="118" height="64" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="368" y="90" width="118" height="64" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="164" y="182" width="254" height="44" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<path d="M214 122 H232 M350 122 H368" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
<text x="155" y="128" font-size="12" fill="#f8fafc" text-anchor="middle">Pitchbook</text>
<text x="291" y="128" font-size="12" fill="#f8fafc" text-anchor="middle">Audit</text>
<text x="427" y="128" font-size="12" fill="#f8fafc" text-anchor="middle">Credit memo</text>
<text x="291" y="210" font-size="12" fill="#cbd5e1" text-anchor="middle">10 finance agents + new data feeds</text>
"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 320" style="background:#0f172a;border-radius:10px;width:100%;max-width:580px">
  <defs><linearGradient id="g{DATE_ID}{rank}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#1e293b"/><stop offset="100%" stop-color="#0f172a"/></linearGradient></defs>
  <rect width="580" height="320" rx="10" fill="url(#g{DATE_ID}{rank})"/>
  <text x="22" y="26" font-size="12" fill="#94a3b8" letter-spacing="1.4">{category} \u00b7 {source}</text>
  <text x="22" y="54" font-size="17" fill="#f8fafc" font-weight="800">{title_line}</text>
  {center}
  <rect x="24" y="236" width="160" height="48" rx="8" fill="#111827" stroke="#334155"/><rect x="24" y="236" width="160" height="4" rx="2" fill="{color}"/><text x="38" y="259" font-size="15" fill="#f8fafc" font-weight="800">#{rank}</text><text x="38" y="276" font-size="10" fill="#94a3b8">ranking</text>
  <rect x="204" y="236" width="160" height="48" rx="8" fill="#111827" stroke="#334155"/><rect x="204" y="236" width="160" height="4" rx="2" fill="{color}"/><text x="218" y="259" font-size="15" fill="#f8fafc" font-weight="800">{html.escape(story["category"])}</text><text x="218" y="276" font-size="10" fill="#94a3b8">category</text>
  <rect x="384" y="236" width="160" height="48" rx="8" fill="#111827" stroke="#334155"/><rect x="384" y="236" width="160" height="4" rx="2" fill="{color}"/><text x="398" y="259" font-size="15" fill="#f8fafc" font-weight="800">{MONTH_DAY}</text><text x="398" y="276" font-size="10" fill="#94a3b8">HKT issue</text>
  <text x="22" y="306" font-size="10" fill="#64748b">Source: {source}</text><text x="558" y="306" font-size="10" fill="#64748b" text-anchor="end">Ken AI Daily</text>
</svg>"""


def render_story_html(story: dict) -> str:
    return f"""<div class="post-card" id="post-{DATE_ID}-{story["rank"]}">
  <div class="post-meta">
    <span class="post-cat" style="background:{story["color"]}">{html.escape(story["category"])}</span>
    <span class="post-source">{html.escape(story["source"])}</span>
    <span class="post-date">{DAY_NAME} \u00b7 {MONTH_DAY}</span>
  </div>
  <h2 class="post-title">{html.escape(story["headline_en"])}</h2>
  <p class="post-title-zh">{html.escape(story["headline_zh"])}</p>
  <p class="post-body">{html.escape(story["body_en"])}</p>
  <p class="post-body post-body-zh">{html.escape(story["body_zh"])}</p>
  <div class="post-infographic">{svg_variant(story)}</div>
  <a class="post-link" href="{html.escape(story["source_url"], quote=True)}" target="_blank" rel="noopener">{html.escape(story["source_label"])}</a>
</div>"""


def render_today_block() -> str:
    parts = [
        f"""<div class="post-card post-visual" id="post-visual-{DATE_ID}">
  <div class="post-meta">
    <span class="post-cat" style="background:#f59e0b">Daily Summary</span>
    <span class="post-date">{DAY_NAME} \u00b7 {MONTH_DAY}</span>
  </div>
  <img src="{SUMMARY_PNG.name}" loading="eager" width="2400" height="1350" alt="Ken AI Daily {DISPLAY_DATE}" style="width:100%;border-radius:8px;margin-top:12px"/>
</div>"""
    ]
    parts.extend(render_story_html(story) for story in STORIES)
    return "\n".join(parts) + "\n"


def render_lead_section() -> str:
    return f"""<section class="lead">
  <div class="lead-inner">
    <div class="lead-text">
      <div class="kicker">{LEAD["kicker"]}</div>
      <h1 class="lead-headline">
        {LEAD["headline_html"]}
      </h1>
      <p class="lead-deck">
        {html.escape(LEAD["deck_en"])}
      </p>
      <p class="lead-deck-zh">
        {html.escape(LEAD["deck_zh"])}
      </p>
      <div class="lead-byline">
        <span><strong>By Ken Chan</strong></span>
        <span class="sep"></span>
        <span>5 min read</span>
        <span class="sep"></span>
        <span>EN \u00b7 \u7e41\u4e2d</span>
        <span class="sep"></span>
        <span style="color: var(--mark);">\u2193 Read below</span>
      </div>
    </div>
    <div class="lead-art">
      <img class="cover-poster" src="{SUMMARY_PNG.name}" width="2400" height="1350" alt="Ken AI Daily {DISPLAY_DATE}" style="width:100%;height:auto;display:block;border-radius:10px;">
    </div>
  </div>
</section>"""


def render_ticker_section() -> str:
    stats = "\n".join(
        f'    <div class="stat"><div class="label">{label}</div><div class="value">{value}</div></div>'
        for label, value in TICKER
    )
    return f"""<section class="ticker">
  <div class="ticker-inner">
{stats}
  </div>
</section>"""


def render_feed_head() -> str:
    return """      <div class="feed-section-head">
        <h2>The <em>Brief</em></h2>
        <span class="count">6 stories \u00b7 May 7, 2026</span>
      </div>"""


def render_masthead_meta() -> str:
    return f"""<div class="masthead-meta">
      <strong>{DAY_NAME}, {DISPLAY_DATE}</strong><br>
      {DISPLAY_DATE}<br>
      <span class="vrule"></span>Hong Kong \u00b7 Updated daily
    </div>"""


def write_summary_png() -> None:
    img = Image.new("RGB", (2400, 1350), "#0b1220")
    draw = ImageDraw.Draw(img)
    title_font = font(FONT_LATIN_BOLD, 106)
    subtitle_font = font(FONT_CJK, 44)
    body_en_font = font(FONT_LATIN, 34)
    body_zh_font = font(FONT_CJK, 30)
    section_font = font(FONT_LATIN_BOLD, 24)

    draw.rounded_rectangle((60, 60, 2340, 1290), radius=42, fill="#101826", outline="#243347", width=3)
    draw.rectangle((60, 60, 1120, 540), fill="#111827")
    draw.polygon([(1680, 150), (2230, 292), (2040, 674), (1490, 520)], fill="#1d4ed8")
    draw.polygon([(1420, 304), (1790, 470), (1680, 824), (1280, 648)], fill="#0f766e")
    draw.rounded_rectangle((120, 120, 860, 184), radius=18, fill="#f59e0b")
    draw.text((150, 130), f"AI News Daily Brief \u00b7 {DAY_NAME}, {DISPLAY_DATE}", font=font(FONT_LATIN_BOLD, 30), fill="#0b1220")
    draw.text((120, 220), "Ken AI Daily", font=title_font, fill="#f8fafc")
    draw.text((120, 340), "AI\u65b0\u805e\u65e5\u5831 \u00b7 \u6bcf\u65e5\u96d9\u8a9e AI \u7cbe\u9078", font=subtitle_font, fill="#cbd5e1")
    draw.text((120, 430), SUMMARY_THEME_EN, font=font(FONT_LATIN_BOLD, 42), fill="#f8fafc")
    draw.text((120, 490), SUMMARY_THEME_ZH, font=subtitle_font, fill="#94a3b8")

    start_y = 610
    row_gap = 102
    for story in STORIES:
        y = start_y + (story["rank"] - 1) * row_gap
        draw.rounded_rectangle((120, y - 10, 2280, y + 74), radius=18, fill="#0f172a", outline=story["color"], width=2)
        draw.text((150, y), f"{story['rank']}.", font=font(FONT_LATIN_BOLD, 34), fill=story["color"])
        en_lines = wrap_by_width(draw, story["headline_en"], body_en_font, 1360)
        zh_lines = wrap_cjk(draw, story["headline_zh"], body_zh_font, 1300)
        draw.text((210, y - 2), en_lines[0], font=body_en_font, fill="#f8fafc")
        draw.text((210, y + 40), zh_lines[0], font=body_zh_font, fill="#94a3b8")
        draw.rounded_rectangle((1830, y, 2270, y + 50), radius=14, fill=story["color"])
        draw.text((1854, y + 10), story["category"], font=section_font, fill="#0b1220")

    draw.text((120, 1235), "kenchankh97.github.io/ai-daily", font=font(FONT_LATIN_BOLD, 28), fill="#f59e0b")
    img.save(SUMMARY_PNG)


def write_top_news_png() -> None:
    top = STORIES[0]
    img = Image.new("RGB", (2400, 1350), "#0b1020")
    draw = ImageDraw.Draw(img)
    title_font = font(FONT_LATIN_BOLD, 82)
    sub_font = font(FONT_CJK, 44)
    body_font = font(FONT_LATIN, 31)
    body_zh_font = font(FONT_CJK, 31)
    pill_font = font(FONT_LATIN_BOLD, 30)
    node_label_font = font(FONT_LATIN_BOLD, 28)
    node_sub_font = font(FONT_LATIN, 22)

    draw.rounded_rectangle((50, 50, 2350, 1300), radius=44, fill="#0f172a", outline=top["color"], width=4)
    draw.rounded_rectangle((100, 100, 770, 180), radius=16, fill=top["color"])
    draw.text((130, 118), top["top_label"], font=pill_font, fill="#0b1220")
    draw.text((100, 238), "Ken AI Daily", font=font(FONT_LATIN_BOLD, 82), fill="#f8fafc")
    draw.text((100, 338), "AI\u65b0\u805e\u65e5\u5831 \u00b7 \u4eca\u65e5\u982d\u689d", font=sub_font, fill="#cbd5e1")

    headline_lines = wrap_by_width(draw, top["headline_en"], title_font, 1240)
    y = draw_lines(draw, headline_lines, (100, 450), title_font, "#f8fafc", 8)
    y = draw_lines(draw, wrap_cjk(draw, top["headline_zh"], sub_font, 1180), (100, y + 10), sub_font, "#94a3b8", 8)
    y += 24

    for bullet in top["top_bullets"]:
        draw.rounded_rectangle((118, y + 8, 138, y + 28), radius=4, fill=top["color"])
        bullet_lines = wrap_by_width(draw, bullet, body_font, 980)
        y = draw_lines(draw, bullet_lines, (165, y), body_font, "#e2e8f0", 4) + 16

    draw.text((100, 1218), top["top_source"], font=font(FONT_LATIN, 24), fill="#94a3b8")

    draw.rounded_rectangle((1460, 170, 2240, 1130), radius=36, fill="#101826", outline="#334155", width=2)
    node_y = [270, 520, 770]
    for idx, (title, subtitle) in enumerate(top["top_nodes"]):
        x1, y1, x2, y2 = 1570, node_y[idx], 2140, node_y[idx] + 110
        draw.rounded_rectangle((x1, y1, x2, y2), radius=26, fill="#111827", outline=top["color"], width=4)
        draw.text((1855, y1 + 36), title, font=node_label_font, fill="#f8fafc", anchor="mm")
        draw.text((1855, y1 + 72), subtitle, font=node_sub_font, fill="#cbd5e1", anchor="mm")

    draw.line((1855, 380, 1855, 520), fill=top["color"], width=8)
    draw.line((1855, 630, 1855, 770), fill=top["color"], width=8)
    draw.rounded_rectangle((1640, 968, 2080, 1050), radius=24, fill="#111827", outline=top["color"], width=4)
    draw.text((1860, 1009), "Pre-release AI gate", font=font(FONT_LATIN_BOLD, 30), fill="#f8fafc", anchor="mm")
    draw.text((1855, 1100), "Ken AI Daily", font=font(FONT_LATIN_BOLD, 28), fill=top["color"], anchor="mm")

    img.save(TOP_NEWS_PNG)


def write_linkedin_post() -> None:
    keycaps = {
        1: "1\ufe0f\u20e3",
        2: "2\ufe0f\u20e3",
        3: "3\ufe0f\u20e3",
        4: "4\ufe0f\u20e3",
        5: "5\ufe0f\u20e3",
        6: "6\ufe0f\u20e3",
    }
    lines = [
        f"AI News Daily Brief \u2014 {DAY_NAME}, {DISPLAY_DATE} \U0001f916",
        "Ken AI Daily | AI\u65b0\u805e\u65e5\u5831 | \u6bcf\u65e5\u96d9\u8a9e AI \u7cbe\u9078",
        "",
        "Ken AI Daily \u2014 bilingual AI news briefing covering AI models, AI agents, AI chips, AI infrastructure, AI funding, AI research, and AI regulation.",
        "",
        LINKEDIN_HOOK,
        "",
        "\u4eca\u65e5\u7126\u9ede / Today's focus:",
        LINKEDIN_FOCUS,
        "",
        "Today's top AI stories:",
        "",
    ]
    for story in STORIES:
        lines.append(f"{keycaps[story['rank']]} {story['emoji']} [{story['category']}] {story['headline_en']}")
        lines.append(f"   {story['headline_zh']}")
        lines.append("")
    lines.extend(
        [
            "Why it matters:",
            LINKEDIN_WHY,
            "",
            "Signal to watch:",
            LINKEDIN_SIGNAL,
            "",
            "Question for the week:",
            LINKEDIN_QUESTION,
            "",
            "Topics: AI models, AI agents, AI chips, AI infrastructure, AI regulation, AI funding, AI research, enterprise AI",
            "",
            "Full digest \U0001f449 https://kenchankh97.github.io/ai-daily/",
            "",
            "#AINews #ArtificialIntelligence #AI #AIAgents #AIInfrastructure #\u79d1\u6280\u65b0\u805e #AI\u65e5\u5831",
        ]
    )
    LINKEDIN_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_index() -> None:
    content = INDEX_PATH.read_text(encoding="utf-8")
    lead_pattern = re.compile(r"<section class=\"lead\">.*?</section>", re.S)
    ticker_pattern = re.compile(r"<section class=\"ticker\">.*?</section>", re.S)
    feed_head_pattern = re.compile(r"      <div class=\"feed-section-head\">.*?</div>", re.S)
    masthead_meta_pattern = re.compile(r"<div class=\"masthead-meta\">.*?</div>", re.S)
    current_marker = f'<div class="post-card post-visual" id="post-visual-{PREVIOUS_DATE_ID}">'
    today_pattern = re.compile(
        rf"<div class=\"post-card post-visual\" id=\"post-visual-{DATE_ID}\">.*?(?={re.escape(current_marker)})",
        re.S,
    )

    if current_marker not in content:
        raise RuntimeError("Could not find the latest issue marker to insert before.")

    content = lead_pattern.sub(render_lead_section(), content, count=1)
    content = ticker_pattern.sub(render_ticker_section(), content, count=1)
    content = feed_head_pattern.sub(render_feed_head(), content, count=1)
    content = masthead_meta_pattern.sub(render_masthead_meta(), content, count=1)
    content = today_pattern.sub("", content)
    content = content.replace(current_marker, render_today_block() + current_marker, 1)
    INDEX_PATH.write_text(content, encoding="utf-8")


def validate() -> dict:
    errors: list[str] = []
    content = INDEX_PATH.read_text(encoding="utf-8")
    linkedin = LINKEDIN_PATH.read_text(encoding="utf-8")

    if f'id="post-visual-{DATE_ID}"' not in content:
        errors.append("missing issue marker")
    if SUMMARY_PNG.name not in content:
        errors.append("missing summary png reference")
    if ".post-visual img" not in content or not any(
        marker in content for marker in ["aspect-ratio:16/9", "aspect-ratio: 16/9", "aspect-ratio: 16 / 9"]
    ):
        errors.append("missing aspect-ratio guard")
    for story in STORIES:
        if story["headline_en"] not in content:
            errors.append(f'missing story in html: {story["rank"]}')
        if story["headline_zh"] not in content:
            errors.append(f'missing zh headline in html: {story["rank"]}')
        if story["source_url"] not in content:
            errors.append(f'missing source url in html: {story["rank"]}')

    required_markers = [
        "1\ufe0f\u20e3",
        "2\ufe0f\u20e3",
        "3\ufe0f\u20e3",
        "4\ufe0f\u20e3",
        "5\ufe0f\u20e3",
        "6\ufe0f\u20e3",
        "Why it matters:",
        "Signal to watch:",
        "Question for the week:",
        "\u4eca\u65e5\u7126\u9ede / Today's focus:",
    ]
    for marker in required_markers:
        if marker not in linkedin:
            errors.append(f"missing linkedin marker: {marker}")

    if "\ufffd" in linkedin or "\ufffd" in content:
        errors.append("replacement character found")

    for image_path in [SUMMARY_PNG, TOP_NEWS_PNG]:
        if not image_path.exists():
            errors.append(f"missing image: {image_path.name}")
            continue
        with Image.open(image_path) as img:
            if img.size != (2400, 1350):
                errors.append(f"bad size for {image_path.name}: {img.size}")

    return {
        "errors": errors,
        "summary_png_bytes": SUMMARY_PNG.stat().st_size if SUMMARY_PNG.exists() else 0,
        "top_news_png_bytes": TOP_NEWS_PNG.stat().st_size if TOP_NEWS_PNG.exists() else 0,
    }


def main() -> None:
    write_summary_png()
    write_top_news_png()
    write_linkedin_post()
    update_index()
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
