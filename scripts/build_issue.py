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
DATE_ID = "20260508"
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
        "category": "AI Agents",
        "color": "#f59e0b",
        "emoji": "\U0001f4b3",
        "source": "AWS",
        "source_label": "AWS \u2192",
        "source_url": "https://aws.amazon.com/blogs/machine-learning/agents-that-transact-introducing-amazon-bedrock-agentcore-payments-built-with-coinbase-and-stripe/",
        "headline_en": "AWS Gives AI Agents Native Payments Through Bedrock AgentCore",
        "headline_zh": "AWS \u8b93 AI \u4ee3\u7406\u53ef\u900f\u904e Bedrock AgentCore \u539f\u751f\u4ed8\u6b3e",
        "body_en": "AWS previewed Bedrock AgentCore Payments so agents can pay for APIs, MCP servers, web content and other agents inside one execution loop. Built with Coinbase and Stripe, the service adds wallet authentication, per-session spending caps and observability, turning agent commerce into governed infrastructure instead of custom billing glue.",
        "body_zh": "AWS \u9810\u89bd Bedrock AgentCore Payments\uff0c\u8b93 AI \u4ee3\u7406\u53ef\u5728\u55ae\u4e00\u57f7\u884c\u8ff4\u5708\u5167\u70ba API\u3001MCP server\u3001\u7db2\u9801\u5167\u5bb9\u8207\u5176\u4ed6\u4ee3\u7406\u4ed8\u6b3e\u3002\u8a72\u670d\u52d9\u7531 Coinbase \u8207 Stripe \u5408\u4f5c\u63d0\u4f9b\uff0c\u52a0\u5165 wallet \u8a8d\u8b49\u3001\u6bcf\u6b21 session \u652f\u51fa\u4e0a\u9650\u8207\u53ef\u89c0\u5bdf\u6027\uff0c\u8b93 agent commerce \u5f9e\u81ea\u5efa\u6536\u6b3e\u908f\u8f2f\u8b8a\u6210\u53ef\u6cbb\u7406\u57fa\u790e\u8a2d\u65bd\u3002",
        "svg_title": "AWS Gives AI Agents Native Payments Through AgentCore",
        "svg_source": "AWS",
        "variant": "payment_rails",
        "top_label": "Top News \u00b7 #1 \u00b7 AI Agents",
        "top_source": "Source: AWS \u00b7 May 7, 2026",
        "top_bullets": [
            "Preview supports paid APIs, MCP servers, web content and other agents.",
            "Coinbase and Stripe provide the wallet infrastructure and payment rails.",
            "Session spending caps and logs keep agent commerce inside guardrails.",
        ],
        "top_nodes": [
            ("Wallet", "limits + auth"),
            ("AgentCore", "x402 loop"),
            ("Tools", "paid endpoints"),
        ],
        "top_footer": "Governed agent commerce",
    },
    {
        "rank": 2,
        "category": "AI Voice",
        "color": "#06b6d4",
        "emoji": "\U0001f3a4",
        "source": "OpenAI",
        "source_label": "OpenAI \u2192",
        "source_url": "https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/",
        "headline_en": "OpenAI Ships Voice Models That Reason, Translate and Transcribe",
        "headline_zh": "OpenAI \u63a8\u51fa\u53ef\u63a8\u7406\u3001\u7ffb\u8b6f\u8207\u8f49\u9304\u7684\u8a9e\u97f3\u6a21\u578b",
        "body_en": "OpenAI launched GPT-Realtime-2, GPT-Realtime-Translate and GPT-Realtime-Whisper in the Realtime API. The new stack adds GPT-5-class reasoning, live translation from 70+ input languages into 13 output languages and streaming speech-to-text, moving voice software from simple turn-taking toward action-oriented interfaces.",
        "body_zh": "OpenAI \u5728 Realtime API \u63a8\u51fa GPT-Realtime-2\u3001GPT-Realtime-Translate \u8207 GPT-Realtime-Whisper\u3002\u65b0\u8a9e\u97f3\u5806\u758a\u52a0\u5165 GPT-5 \u7d1a\u63a8\u7406\uff0c\u652f\u63f4 70 \u591a\u7a2e\u8f38\u5165\u8a9e\u8a00\u81f3 13 \u7a2e\u8f38\u51fa\u8a9e\u8a00\u7684\u5373\u6642\u7ffb\u8b6f\uff0c\u4ee5\u53ca streaming speech-to-text\uff0c\u8b93\u8a9e\u97f3\u8edf\u4ef6\u5f9e\u55ae\u7d14\u5c0d\u7b54\u8f49\u5411\u53ef\u57f7\u884c\u5de5\u4f5c\u7684\u4ecb\u9762\u3002",
        "svg_title": "OpenAI Ships Voice Models That Reason and Translate",
        "svg_source": "OpenAI",
        "variant": "voice_stack",
    },
    {
        "rank": 3,
        "category": "AI Infrastructure",
        "color": "#ef4444",
        "emoji": "\U0001f517",
        "source": "AWS",
        "source_label": "AWS \u2192",
        "source_url": "https://aws.amazon.com/blogs/aws/the-aws-mcp-server-is-now-generally-available/",
        "headline_en": "AWS MCP Server Reaches GA for Secure Agent Access to Cloud APIs",
        "headline_zh": "AWS MCP Server \u6b63\u5f0f\u4e0a\u5e02\uff0c\u8b93\u4ee3\u7406\u5b89\u5168\u9023\u63a5\u96f2\u7aef API",
        "body_en": "AWS made its managed MCP Server generally available, giving agents secure authenticated access to 15,000+ AWS APIs plus live documentation retrieval and sandboxed server-side scripting. The launch shows cloud vendors want agent access to become auditable infrastructure instead of a local credential hack.",
        "body_zh": "AWS \u5c07\u5176 managed MCP Server \u63a8\u5411 GA\uff0c\u8b93 AI \u4ee3\u7406\u53ef\u5b89\u5168\u5730\u4f7f\u7528 15,000 \u591a\u500b AWS API\uff0c\u540c\u6642\u53d6\u5f97\u5373\u6642\u6587\u4ef6\u6aa2\u7d22\u8207 sandboxed server-side scripting\u3002\u9019\u6b21\u767c\u5e03\u986f\u793a\u96f2\u5ee0\u5546\u6b63\u8a66\u5716\u5c07 agent access \u8b8a\u6210\u53ef\u7a3d\u6838\u7684\u57fa\u790e\u8a2d\u65bd\uff0c\u800c\u4e0d\u662f\u672c\u6a5f\u6191\u8b49 workaround\u3002",
        "svg_title": "AWS MCP Server Reaches GA for Secure Agent Access",
        "svg_source": "AWS",
        "variant": "mcp_bridge",
    },
    {
        "rank": 4,
        "category": "Enterprise AI",
        "color": "#f97316",
        "emoji": "\U0001f3e2",
        "source": "IBM",
        "source_label": "IBM \u2192",
        "source_url": "https://www.ibm.com/new/announcements/ibm-announcements-at-think-2026",
        "headline_en": "IBM Unveils an Agentic Control Plane and AI Stack at Think 2026",
        "headline_zh": "IBM \u5728 Think 2026 \u63a8\u51fa\u4ee3\u7406\u63a7\u5236\u5e73\u9762\u8207 AI \u5806\u758a",
        "body_en": "IBM used Think 2026 to push watsonx Orchestrate as a unified agentic control plane, alongside AI editions across core software, agentic data integration and MCP-enabled watsonx.data. The message is that enterprises are now buying governed orchestration layers, not isolated copilots.",
        "body_zh": "IBM \u5728 Think 2026 \u5c07 watsonx Orchestrate \u5b9a\u4f4d\u70ba\u7d71\u4e00\u7684 agentic control plane\uff0c\u4e26\u540c\u6b65\u63a8\u51fa\u6db5\u84cb core software \u7684 AI editions\u3001agentic data integration \u8207\u652f\u63f4 MCP \u7684 watsonx.data\u3002\u9019\u4ee3\u8868\u4f01\u696d\u958b\u59cb\u8cfc\u8cb7\u53ef\u6cbb\u7406\u7684 orchestration layer\uff0c\u800c\u4e0d\u662f\u55ae\u9ede copilots\u3002",
        "svg_title": "IBM Unveils an Agentic Control Plane at Think 2026",
        "svg_source": "IBM",
        "variant": "enterprise_control",
    },
    {
        "rank": 5,
        "category": "AI Adoption",
        "color": "#22c55e",
        "emoji": "\U0001f4ca",
        "source": "Microsoft",
        "source_label": "Microsoft \u2192",
        "source_url": "https://blogs.microsoft.com/on-the-issues/2026/05/07/the-state-of-global-ai-diffusion-in-2026/",
        "headline_en": "Microsoft Says Global AI Use Climbed to 17.8% in Q1 2026",
        "headline_zh": "Microsoft \u6307 2026 \u5e74\u7b2c\u4e00\u5b63\u5168\u7403 AI \u4f7f\u7528\u7387\u5347\u81f3 17.8%",
        "body_en": "Microsoft's latest Global AI Diffusion Report said AI usage among the world's working-age population rose from 16.3% to 17.8% in Q1 2026, with 26 economies now above 30% and global git pushes up 78% year over year. Adoption is no longer anecdotal; it is becoming measurable economic infrastructure.",
        "body_zh": "Microsoft \u6700\u65b0\u7684 Global AI Diffusion Report \u6307\u51fa\uff0c2026 \u5e74\u7b2c\u4e00\u5b63\u5168\u7403\u52de\u52d5\u5e74\u9f61\u4eba\u53e3\u7684 AI \u4f7f\u7528\u7387\u7531 16.3% \u5347\u81f3 17.8%\uff0c\u73fe\u5df2\u6709 26 \u500b\u7d93\u6fdf\u9ad4\u8d85\u904e 30%\uff0c\u800c\u5168\u7403 git pushes \u4ea6\u6309\u5e74\u5927\u589e 78%\u3002AI \u63a1\u7528\u5df2\u4e0d\u518d\u53ea\u662f\u611f\u89ba\u6216 anecdotes\uff0c\u800c\u6b63\u5728\u6210\u70ba\u53ef\u6e2c\u91cf\u7684\u7d93\u6fdf\u57fa\u790e\u8a2d\u65bd\u3002",
        "svg_title": "Microsoft Says Global AI Use Climbed to 17.8%",
        "svg_source": "Microsoft",
        "variant": "adoption_map",
    },
    {
        "rank": 6,
        "category": "AI Regulation",
        "color": "#14b8a6",
        "emoji": "\U0001f6e1\ufe0f",
        "source": "NIST / CAISI",
        "source_label": "NIST \u2192",
        "source_url": "https://www.nist.gov/news-events/news/2026/05/caisi-signs-agreements-regarding-frontier-ai-national-security-testing",
        "headline_en": "NIST Expands CAISI Testing Deals With Google DeepMind, Microsoft and xAI",
        "headline_zh": "NIST \u64f4\u5927 CAISI \u8207 Google DeepMind\u3001Microsoft\u3001xAI \u7684\u6e2c\u8a66\u5354\u8b70",
        "body_en": "NIST said CAISI signed new agreements for pre-deployment evaluations, classified-environment testing and targeted research with Google DeepMind, Microsoft and xAI. As governments gain earlier access to unreleased models, frontier AI launches are starting to look more like regulated product approvals.",
        "body_zh": "NIST \u8868\u793a\uff0cCAISI \u5df2\u8207 Google DeepMind\u3001Microsoft \u53ca xAI \u7c3d\u7f72\u65b0\u5354\u8b70\uff0c\u6db5\u84cb\u767c\u5e03\u524d\u8a55\u4f30\u3001\u6a5f\u5bc6\u74b0\u5883\u6e2c\u8a66\u8207\u91dd\u5c0d\u6027\u7814\u7a76\u3002\u96a8\u8457\u653f\u5e9c\u80fd\u66f4\u65e9\u63a5\u89f8\u5c1a\u672a\u516c\u958b\u7684\u6a21\u578b\uff0c\u524d\u6cbf AI \u767c\u5e03\u958b\u59cb\u8d8a\u4f86\u8d8a\u50cf\u53d7\u76e3\u7ba1\u7684\u7522\u54c1\u5be9\u6279\u6d41\u7a0b\u3002",
        "svg_title": "CAISI Expands Frontier AI Pre-Deployment Testing",
        "svg_source": "NIST / CAISI",
        "variant": "policy_gate",
    },
]


LEAD = {
    "kicker": f"The Cover Story \u00b7 {MONTH_DAY}",
    "headline_html": "AI is turning into a <em>governed operating stack for voice, tools, payments and launch control.</em>",
    "deck_en": "From native agent payments and realtime voice models to secure MCP access, enterprise control planes, rising global usage and government pre-release testing, today's AI market is shifting from isolated demos toward connected, measurable and governed production systems.",
    "deck_zh": "\u5f9e\u539f\u751f agent \u4ed8\u6b3e\u3001\u5373\u6642\u8a9e\u97f3\u6a21\u578b\uff0c\u5230\u5b89\u5168\u7684 MCP \u9023\u63a5\u3001\u4f01\u696d\u63a7\u5236\u5e73\u9762\u3001\u4e0a\u5347\u7684\u5168\u7403\u4f7f\u7528\u7387\u8207\u653f\u5e9c\u7684\u767c\u5e03\u524d\u6e2c\u8a66\uff0cAI \u5e02\u5834\u6b63\u7531\u5b64\u7acb demo \u8f49\u5411\u76f8\u4e92\u9023\u63a5\u3001\u53ef\u91cf\u5316\u53ca\u53ef\u6cbb\u7406\u7684 production \u7cfb\u7d71\u3002",
}

TICKER = [
    ("Agent payments", "x402<span class=\"small\">+ session caps</span>"),
    ("Realtime voice", "70+<span class=\"small\">input languages</span>"),
    ("AWS MCP", "15k+<span class=\"small\">API operations</span>"),
    ("AI diffusion", "17.8%<span class=\"small\">global usage</span>"),
]

LINKEDIN_HOOK = "AI is no longer just a model contest. The new race is over who owns the payment rails, voice layer, tool access and launch controls around intelligent systems."
LINKEDIN_FOCUS = "Today's six stories show AI becoming a governed operating stack: agents can now pay, voice interfaces can reason in real time, cloud platforms are standardizing secure tool access, enterprises are buying control planes, adoption is measurable, and governments want pre-release visibility."
LINKEDIN_WHY = "For leaders, the advantage is shifting beyond raw model IQ. The winners will pair strong models with trusted interfaces, auditable execution paths, policy controls and the infrastructure needed to put AI into real workflows without losing oversight."
LINKEDIN_SIGNAL = "Watch the next wave of competition move into orchestration, observability, identity and payment infrastructure. AI products that cannot plug into governed operating stacks will look increasingly incomplete."
LINKEDIN_QUESTION = "What will create more durable value in 2026: a better model, or better control over how agents talk, pay and act?"

SUMMARY_THEME_EN = "AI is becoming a governed operating stack for work."
SUMMARY_THEME_ZH = "AI \u6b63\u5728\u8b8a\u6210\u53ef\u6cbb\u7406\u7684\u5de5\u4f5c\u904b\u4f5c\u5806\u758a\u3002"


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
    elif story["variant"] == "payment_rails":
        center = f"""
<rect x="72" y="98" width="126" height="82" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="226" y="76" width="128" height="126" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="382" y="98" width="126" height="82" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M198 139 H226 M354 139 H382" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="135" y="131" font-size="16" fill="#f8fafc" text-anchor="middle">Wallet</text>
<text x="135" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">limits + auth</text>
<text x="290" y="128" font-size="16" fill="#f8fafc" text-anchor="middle">AgentCore</text>
<text x="290" y="151" font-size="11" fill="#cbd5e1" text-anchor="middle">x402 payment loop</text>
<text x="445" y="131" font-size="16" fill="#f8fafc" text-anchor="middle">Tools</text>
<text x="445" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">paid endpoints</text>
"""
    elif story["variant"] == "voice_stack":
        center = f"""
<circle cx="132" cy="138" r="42" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M114 118 Q132 100 150 118 Q132 136 114 154" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
<rect x="236" y="84" width="118" height="108" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="392" y="98" width="104" height="82" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M174 138 H236 M354 138 H392" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="132" y="146" font-size="16" fill="#f8fafc" text-anchor="middle">Voice</text>
<text x="295" y="128" font-size="16" fill="#f8fafc" text-anchor="middle">Reason</text>
<text x="295" y="152" font-size="11" fill="#cbd5e1" text-anchor="middle">translate + transcribe</text>
<text x="444" y="131" font-size="16" fill="#f8fafc" text-anchor="middle">Action</text>
<text x="444" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">realtime apps</text>
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
    elif story["variant"] == "mcp_bridge":
        center = f"""
<rect x="74" y="98" width="120" height="82" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="230" y="82" width="120" height="114" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="386" y="98" width="120" height="82" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M194 139 H230 M350 139 H386" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="134" y="131" font-size="15" fill="#f8fafc" text-anchor="middle">Agent</text>
<text x="134" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">IAM auth</text>
<text x="290" y="128" font-size="15" fill="#f8fafc" text-anchor="middle">MCP Server</text>
<text x="290" y="151" font-size="11" fill="#cbd5e1" text-anchor="middle">docs + run_script</text>
<text x="446" y="131" font-size="15" fill="#f8fafc" text-anchor="middle">AWS APIs</text>
<text x="446" y="154" font-size="11" fill="#cbd5e1" text-anchor="middle">15k+ operations</text>
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
    elif story["variant"] == "enterprise_control":
        center = f"""
<rect x="88" y="90" width="128" height="86" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="228" y="76" width="124" height="114" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="364" y="90" width="128" height="86" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M216 133 H228 M352 133 H364" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="152" y="126" font-size="14" fill="#f8fafc" text-anchor="middle">Apps</text>
<text x="152" y="148" font-size="11" fill="#cbd5e1" text-anchor="middle">data + workflows</text>
<text x="290" y="125" font-size="14" fill="#f8fafc" text-anchor="middle">Control plane</text>
<text x="290" y="148" font-size="11" fill="#cbd5e1" text-anchor="middle">observe + govern</text>
<text x="428" y="126" font-size="14" fill="#f8fafc" text-anchor="middle">Agents</text>
<text x="428" y="148" font-size="11" fill="#cbd5e1" text-anchor="middle">secure execution</text>
"""
    elif story["variant"] == "adoption_map":
        center = f"""
<rect x="112" y="116" width="64" height="82" rx="12" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="214" y="96" width="64" height="102" rx="12" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="316" y="72" width="64" height="126" rx="12" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="410" y="98" width="90" height="80" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<text x="144" y="145" font-size="12" fill="#f8fafc" text-anchor="middle">16.3%</text>
<text x="144" y="166" font-size="10" fill="#cbd5e1" text-anchor="middle">Q4 2025</text>
<text x="246" y="135" font-size="12" fill="#f8fafc" text-anchor="middle">17.8%</text>
<text x="246" y="156" font-size="10" fill="#cbd5e1" text-anchor="middle">Q1 2026</text>
<text x="348" y="121" font-size="12" fill="#f8fafc" text-anchor="middle">26</text>
<text x="348" y="142" font-size="10" fill="#cbd5e1" text-anchor="middle">economies</text>
<text x="455" y="128" font-size="12" fill="#f8fafc" text-anchor="middle">Git pushes</text>
<text x="455" y="150" font-size="12" fill="#f8fafc" text-anchor="middle">+78% YoY</text>
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
    return f"""      <div class="feed-section-head">
        <h2>The <em>Brief</em></h2>
        <span class="count">6 stories \u00b7 {DISPLAY_DATE}</span>
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
    draw.text((1860, 1009), top.get("top_footer", "Top AI signal"), font=font(FONT_LATIN_BOLD, 30), fill="#f8fafc", anchor="mm")
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
