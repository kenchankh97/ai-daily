#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import textwrap
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"
LINKEDIN_PATH = ROOT / "linkedin-post.txt"
SUMMARY_PNG = ROOT / "ai-daily-20260505.png"
TOP_NEWS_PNG = ROOT / "ai-daily-20260505-top-news.png"

DATE_ID = "20260505"
DISPLAY_DATE = "May 5, 2026"
DAY_NAME = "Tuesday"

FONT_CJK = Path("C:/Windows/Fonts/msjh.ttc")
FONT_LATIN_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
FONT_LATIN = Path("C:/Windows/Fonts/segoeui.ttf")

STORIES = [
    {
        "rank": 1,
        "category": "AI Regulation",
        "color": "#f59e0b",
        "emoji": "🏛️",
        "source": "Reuters / NYT",
        "source_label": "Reuters / Investing ↗",
        "source_url": "https://www.investing.com/news/stock-market-news/white-house-considers-vetting-ai-models-before-they-are-released-nyt-reports-4657192",
        "headline_en": "White House Weighs Pre-Release Vetting for New AI Models",
        "headline_zh": "白宮考慮要求新 AI 模型在發布前接受審查",
        "body_en": "Reuters reported that the White House is considering government oversight for new AI models, including an executive-order working group that would bring together tech executives and officials to examine oversight procedures. Even before any rule is finalized, the signal is clear: frontier-model policy may move upstream from harms to pre-release controls.",
        "body_zh": "路透引述《紐約時報》報道，白宮正考慮對新 AI 模型引入政府監督，並可能透過行政命令成立工作小組，集合科技公司高層與官員研究審查程序。即使政策尚未定案，訊號已很清楚：前沿模型監管可能從事後追責，轉向發布前把關。",
        "svg_title": "White House Weighs Pre-Release Vetting for New AI Models",
        "svg_source": "Reuters / NYT",
        "variant": "policy_gate",
    },
    {
        "rank": 2,
        "category": "Enterprise AI",
        "color": "#14b8a6",
        "emoji": "🤝",
        "source": "Anthropic",
        "source_label": "Anthropic ↗",
        "source_url": "https://www.anthropic.com/news/enterprise-ai-services-company",
        "headline_en": "Anthropic Launches Enterprise AI Services Company With Wall Street Backers",
        "headline_zh": "Anthropic 聯手華爾街資本成立企業 AI 服務公司",
        "body_en": "Anthropic, Blackstone, Hellman & Friedman, and Goldman Sachs announced a new AI services company that will bring Claude into the core operations of mid-sized businesses, with Anthropic engineers embedded alongside the delivery team. The move shows frontier labs are pushing beyond APIs into service-heavy enterprise rollouts.",
        "body_zh": "Anthropic 與 Blackstone、Hellman & Friedman 及 Goldman Sachs 宣布成立新的 AI 服務公司，協助中型企業把 Claude 部署到核心營運流程，並由 Anthropic 工程師深度參與交付。這代表前沿 AI 公司正從單純賣模型，走向高接觸度的企業導入服務。",
        "svg_title": "Anthropic Launches Enterprise AI Services Company With Wall Street Backers",
        "svg_source": "Anthropic",
        "variant": "enterprise_chain",
    },
    {
        "rank": 3,
        "category": "AI Funding",
        "color": "#22c55e",
        "emoji": "💼",
        "source": "Bloomberg / Investing.com",
        "source_label": "Bloomberg / Investing ↗",
        "source_url": "https://m.za.investing.com/news/stock-market-news/openai-secures-4-billion-for-new-joint-venture-with-pe-giants-bloomberg-reports-4250177?ampMode=1",
        "headline_en": "OpenAI Reportedly Secures More Than $4B for The Deployment Company",
        "headline_zh": "OpenAI 據報為 The Deployment Company 籌得逾 40 億美元",
        "body_en": "According to Bloomberg, OpenAI has secured more than $4 billion for a new venture called The Deployment Company, valuing the entity at $10 billion while OpenAI keeps majority ownership and control. The financing suggests the next AI capital wave is flowing into rollout capacity, not just frontier research.",
        "body_zh": "據 Bloomberg 報道，OpenAI 已為名為 The Deployment Company 的新合資平台籌得逾 40 億美元，該實體估值約 100 億美元，且 OpenAI 仍保有多數股權與控制權。這顯示下一波 AI 資本正流向企業部署能力，而不只是前沿研究本身。",
        "svg_title": "OpenAI Reportedly Secures More Than $4B for The Deployment Company",
        "svg_source": "Bloomberg / Investing.com",
        "variant": "funding_stack",
    },
    {
        "rank": 4,
        "category": "AI Chips",
        "color": "#6366f1",
        "emoji": "🧠",
        "source": "Cerebras",
        "source_label": "Cerebras ↗",
        "source_url": "https://www.cerebras.ai/press-release/cerebras-systems-announces-launch-of-initial-public-offering",
        "headline_en": "Cerebras Starts IPO Roadshow as AI Inference Demand Lifts Chip Ambitions",
        "headline_zh": "Cerebras 啟動 IPO 路演，AI 推理需求推高晶片雄心",
        "body_en": "Cerebras said it plans to offer 28 million shares at $115 to $125 each, with an additional 4.2 million share option for underwriters. That puts one of AI's most visible inference-chip challengers in front of public-market investors just as compute demand shifts from training toward serving models at scale.",
        "body_zh": "Cerebras 表示計劃以每股 115 至 125 美元發售 2,800 萬股，另設 420 萬股超額配售選擇權。這讓這家最受矚目的 AI 推理晶片挑戰者，在市場需求由訓練轉向大規模推理服務之際，正式接受公開市場定價。",
        "svg_title": "Cerebras Starts IPO Roadshow as AI Inference Demand Lifts Chip Ambitions",
        "svg_source": "Cerebras",
        "variant": "chip_market",
    },
    {
        "rank": 5,
        "category": "AI Infrastructure",
        "color": "#a855f7",
        "emoji": "🔌",
        "source": "Reuters",
        "source_label": "Reuters / Investing ↗",
        "source_url": "https://www.investing.com/news/stock-market-news/lattice-semiconductor-to-buy-software-firm-ami-in-165-billion-deal-4657413",
        "headline_en": "Lattice to Buy AMI for $1.65 Billion in AI Platform Management Push",
        "headline_zh": "Lattice 擬以 16.5 億美元收購 AMI，強化 AI 平台管理布局",
        "body_en": "Reuters reported that Lattice Semiconductor will acquire AI cloud and platform management firm AMI for $1.65 billion. The deal matters because chip and infrastructure companies are increasingly buying the software control layer that sits between silicon, servers and enterprise AI operations.",
        "body_zh": "路透報道指出，Lattice Semiconductor 將以 16.5 億美元收購 AI 雲端與平台管理公司 AMI。這筆交易的重要性在於，晶片與基礎設施公司正愈來愈積極補上位於矽晶片、伺服器與企業 AI 營運之間的軟件控制層。",
        "svg_title": "Lattice to Buy AMI for $1.65 Billion in AI Platform Management Push",
        "svg_source": "Reuters",
        "variant": "infra_grid",
    },
    {
        "rank": 6,
        "category": "AI Models",
        "color": "#ef4444",
        "emoji": "🛠️",
        "source": "AWS",
        "source_label": "AWS ↗",
        "source_url": "https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-ai-ai/",
        "headline_en": "AWS Adds an Agentic SageMaker Flow for Model Customization",
        "headline_zh": "AWS 為 SageMaker 加入代理式模型客製化流程",
        "body_en": "AWS launched a SageMaker AI agent experience that turns model customization into a guided workflow spanning use-case framing, data transformation, evaluation, and deployment to Bedrock or SageMaker endpoints. The launch shows the major clouds are productizing the entire tuning pipeline, not just the model endpoint.",
        "body_zh": "AWS 推出 SageMaker AI 代理式體驗，把模型客製化變成一條可引導的工作流，涵蓋需求定義、資料轉換、評估，以及部署到 Bedrock 或 SageMaker 端點。這代表大型雲平台正把整條模型調校管線產品化，而不只是提供推理端點。",
        "svg_title": "AWS Adds an Agentic SageMaker Flow for Model Customization",
        "svg_source": "AWS",
        "variant": "workflow_map",
    },
]


LEAD = {
    "kicker": "The Cover Story · May 5",
    "headline_html": "AI is shifting from <em>model launches to deployment control.</em>",
    "deck_en": "White House oversight talk, Anthropic and OpenAI deployment vehicles, a Cerebras IPO, Lattice's AMI deal and AWS's new SageMaker agent workflow all point to the same change: the next AI race is about regulation, rollout and operating leverage.",
    "deck_zh": "白宮監管訊號、Anthropic 與 OpenAI 的部署平台、Cerebras IPO、Lattice 收購 AMI，以及 AWS 新的 SageMaker 代理式工作流，都指向同一件事：下一場 AI 競賽重點不再只是模型發布，而是監管、部署與營運槓桿。",
}

TICKER = [
    ("White House AI", "EO?<span class=\"small\">working group</span>"),
    ("Anthropic services", "$1.5B<span class=\"small\">new vehicle</span>"),
    ("OpenAI deployment", "$4B+<span class=\"small\">reported</span>"),
    ("Cerebras IPO", "$3.5B<span class=\"small\">roadshow</span>"),
]

LINKEDIN_HOOK = "AI is entering its control-layer era: regulators, private equity, chip markets and cloud platforms are all racing to decide how frontier systems get deployed at scale."
LINKEDIN_FOCUS = "The biggest AI shift today is not a new benchmark. It is the buildout of the systems that approve, finance, tune, package and distribute AI into real-world operations."
LINKEDIN_WHY = "For executives, builders and investors, the new moat is no longer just raw model quality. It is who can move AI safely from research into audited workflows, funded rollouts, and production infrastructure."
LINKEDIN_SIGNAL = "Watch for 'deployment infrastructure' to become its own AI category: services firms, oversight processes, tuning agents, and platform-management software are now attracting policy attention and multibillion-dollar capital."
LINKEDIN_QUESTION = "Which layer becomes more valuable over the next 12 months: the frontier model itself, or the operating system around deployment?"


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
    title = html.escape(story["svg_title"])
    category = html.escape(story["category"].upper())
    source = html.escape(story["svg_source"])
    color = story["color"]
    rank = story["rank"]
    if story["variant"] == "policy_gate":
        center = """
<rect x="86" y="92" width="128" height="92" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="226" y="78" width="128" height="120" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="366" y="92" width="128" height="92" rx="16" fill="#111827" stroke="{color}" stroke-width="4"/>
<path d="M214 138 H226 M354 138 H366" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<text x="150" y="145" font-size="18" fill="#f8fafc" text-anchor="middle">Labs</text>
<text x="290" y="132" font-size="18" fill="#f8fafc" text-anchor="middle">Review</text>
<text x="290" y="157" font-size="12" fill="#cbd5e1" text-anchor="middle">working group</text>
<text x="430" y="145" font-size="18" fill="#f8fafc" text-anchor="middle">Release</text>
""".format(color=color)
    elif story["variant"] == "enterprise_chain":
        center = """
<circle cx="122" cy="140" r="40" fill="#111827" stroke="{color}" stroke-width="4"/><text x="122" y="146" font-size="15" fill="#f8fafc" text-anchor="middle">Claude</text>
<rect x="214" y="100" width="152" height="80" rx="14" fill="#111827" stroke="{color}" stroke-width="4"/>
<text x="290" y="132" font-size="17" fill="#f8fafc" text-anchor="middle">Applied AI</text><text x="290" y="156" font-size="12" fill="#cbd5e1" text-anchor="middle">embedded delivery</text>
<rect x="414" y="86" width="92" height="36" rx="10" fill="#111827" stroke="{color}" stroke-width="3"/><text x="460" y="109" font-size="11" fill="#f8fafc" text-anchor="middle">PE firms</text>
<rect x="414" y="130" width="92" height="36" rx="10" fill="#111827" stroke="{color}" stroke-width="3"/><text x="460" y="153" font-size="11" fill="#f8fafc" text-anchor="middle">Ops teams</text>
<rect x="414" y="174" width="92" height="36" rx="10" fill="#111827" stroke="{color}" stroke-width="3"/><text x="460" y="197" font-size="11" fill="#f8fafc" text-anchor="middle">Mid-market</text>
<path d="M162 140 H214 M366 140 H414" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
""".format(color=color)
    elif story["variant"] == "funding_stack":
        center = """
<rect x="120" y="170" width="340" height="28" rx="8" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="150" y="134" width="280" height="28" rx="8" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="180" y="98" width="220" height="28" rx="8" fill="#111827" stroke="{color}" stroke-width="3"/>
<text x="290" y="117" font-size="13" fill="#f8fafc" text-anchor="middle">OpenAI control</text>
<text x="290" y="153" font-size="13" fill="#f8fafc" text-anchor="middle">$4B+ investor capital</text>
<text x="290" y="189" font-size="13" fill="#f8fafc" text-anchor="middle">$10B deployment vehicle</text>
<path d="M290 78 V98" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
<circle cx="290" cy="68" r="10" fill="{color}"/>
""".format(color=color)
    elif story["variant"] == "chip_market":
        center = """
<rect x="110" y="86" width="170" height="118" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<rect x="300" y="86" width="170" height="118" rx="18" fill="#111827" stroke="{color}" stroke-width="4"/>
<text x="195" y="132" font-size="24" fill="#f8fafc" font-weight="900" text-anchor="middle">CBRS</text>
<text x="195" y="160" font-size="13" fill="#cbd5e1" text-anchor="middle">IPO roadshow</text>
<polyline points="320,176 352,148 382,156 414,118 446,132" fill="none" stroke="{color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="446" cy="132" r="10" fill="{color}"/>
<text x="385" y="104" font-size="12" fill="#cbd5e1" text-anchor="middle">$115-$125</text>
""".format(color=color)
    elif story["variant"] == "infra_grid":
        center = """
<rect x="94" y="92" width="114" height="54" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="236" y="92" width="114" height="54" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="378" y="92" width="114" height="54" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="165" y="164" width="114" height="54" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="307" y="164" width="114" height="54" rx="12" fill="#111827" stroke="{color}" stroke-width="3"/>
<path d="M208 119 H236 M350 119 H378 M222 164 L236 146 M358 164 L350 146 M279 191 H307" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
<text x="151" y="124" font-size="12" fill="#f8fafc" text-anchor="middle">Silicon</text>
<text x="293" y="124" font-size="12" fill="#f8fafc" text-anchor="middle">Firmware</text>
<text x="435" y="124" font-size="12" fill="#f8fafc" text-anchor="middle">Cloud</text>
<text x="222" y="196" font-size="12" fill="#f8fafc" text-anchor="middle">Mgmt</text>
<text x="364" y="196" font-size="12" fill="#f8fafc" text-anchor="middle">Ops</text>
""".format(color=color)
    else:
        center = """
<rect x="82" y="98" width="116" height="72" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="232" y="98" width="116" height="72" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<rect x="382" y="98" width="116" height="72" rx="14" fill="#111827" stroke="{color}" stroke-width="3"/>
<text x="140" y="141" font-size="13" fill="#f8fafc" text-anchor="middle">Prompt</text>
<text x="290" y="141" font-size="13" fill="#f8fafc" text-anchor="middle">Tune</text>
<text x="440" y="141" font-size="13" fill="#f8fafc" text-anchor="middle">Deploy</text>
<path d="M198 134 H232 M348 134 H382" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
<rect x="202" y="192" width="176" height="26" rx="8" fill="#111827" stroke="{color}" stroke-width="3"/>
<text x="290" y="210" font-size="11" fill="#cbd5e1" text-anchor="middle">agents + evaluation + endpoints</text>
""".format(color=color)

    title_line = html.escape(textwrap.shorten(story["svg_title"], width=62, placeholder="…"))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 320" style="background:#0f172a;border-radius:10px;width:100%;max-width:580px">
  <defs><linearGradient id="g{DATE_ID}{rank}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#1e293b"/><stop offset="100%" stop-color="#0f172a"/></linearGradient></defs>
  <rect width="580" height="320" rx="10" fill="url(#g{DATE_ID}{rank})"/>
  <text x="22" y="26" font-size="12" fill="#94a3b8" letter-spacing="1.4">{category} · {html.escape(source)}</text>
  <text x="22" y="54" font-size="17" fill="#f8fafc" font-weight="800">{title_line}</text>
  {center}
  <rect x="24" y="236" width="160" height="48" rx="8" fill="#111827" stroke="#334155"/><rect x="24" y="236" width="160" height="4" rx="2" fill="{color}"/><text x="38" y="259" font-size="15" fill="#f8fafc" font-weight="800">#{rank}</text><text x="38" y="276" font-size="10" fill="#94a3b8">ranking</text>
  <rect x="204" y="236" width="160" height="48" rx="8" fill="#111827" stroke="#334155"/><rect x="204" y="236" width="160" height="4" rx="2" fill="{color}"/><text x="218" y="259" font-size="15" fill="#f8fafc" font-weight="800">{html.escape(story["category"])}</text><text x="218" y="276" font-size="10" fill="#94a3b8">category</text>
  <rect x="384" y="236" width="160" height="48" rx="8" fill="#111827" stroke="#334155"/><rect x="384" y="236" width="160" height="4" rx="2" fill="{color}"/><text x="398" y="259" font-size="15" fill="#f8fafc" font-weight="800">May 5</text><text x="398" y="276" font-size="10" fill="#94a3b8">HKT issue</text>
  <text x="22" y="306" font-size="10" fill="#64748b">Source: {source}</text><text x="558" y="306" font-size="10" fill="#64748b" text-anchor="end">Ken AI Daily</text>
</svg>"""


def render_story_html(story: dict) -> str:
    return f"""<div class="post-card" id="post-{DATE_ID}-{story["rank"]}">
  <div class="post-meta">
    <span class="post-cat" style="background:{story["color"]}">{html.escape(story["category"])}</span>
    <span class="post-source">{html.escape(story["source"])}</span>
    <span class="post-date">{DAY_NAME} · May 5</span>
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
    <span class="post-date">{DAY_NAME} · May 5</span>
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
        <span>EN · 繁中</span>
        <span class="sep"></span>
        <span style="color: var(--mark);">↓ Read below</span>
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
        <span class="count">6 stories · May 5, 2026</span>
      </div>"""


def write_summary_png() -> None:
    img = Image.new("RGB", (2400, 1350), "#0b1220")
    draw = ImageDraw.Draw(img)
    title_font = font(FONT_LATIN_BOLD, 108)
    subtitle_font = font(FONT_CJK, 44)
    body_en_font = font(FONT_LATIN, 36)
    body_zh_font = font(FONT_CJK, 30)
    section_font = font(FONT_LATIN_BOLD, 26)

    draw.rounded_rectangle((60, 60, 2340, 1290), radius=42, fill="#101826", outline="#243347", width=3)
    draw.rectangle((60, 60, 1100, 540), fill="#111827")
    draw.polygon([(1700, 150), (2220, 300), (2030, 660), (1520, 520)], fill="#1d4ed8")
    draw.polygon([(1440, 300), (1810, 470), (1700, 800), (1320, 650)], fill="#0f766e")
    draw.rounded_rectangle((120, 120, 820, 184), radius=18, fill="#f59e0b")
    draw.text((150, 130), "AI News Daily Brief · Tuesday, May 5, 2026", font=font(FONT_LATIN_BOLD, 30), fill="#0b1220")
    draw.text((120, 220), "Ken AI Daily", font=title_font, fill="#f8fafc")
    draw.text((120, 340), "AI新聞日報 · 每日雙語 AI 精選", font=subtitle_font, fill="#cbd5e1")

    theme = "Deployment control is becoming the new AI battleground."
    theme_zh = "部署控制層，正成為新的 AI 主戰場。"
    draw.text((120, 430), theme, font=font(FONT_LATIN_BOLD, 44), fill="#f8fafc")
    draw.text((120, 490), theme_zh, font=subtitle_font, fill="#94a3b8")

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
        draw.rounded_rectangle((1845, y, 2260, y + 50), radius=14, fill=story["color"])
        draw.text((1870, y + 8), story["category"], font=section_font, fill="#0b1220")

    draw.text((120, 1235), "kenchankh97.github.io/ai-daily", font=font(FONT_LATIN_BOLD, 28), fill="#f59e0b")
    img.save(SUMMARY_PNG)


def write_top_news_png() -> None:
    top = STORIES[0]
    img = Image.new("RGB", (2400, 1350), "#0b1020")
    draw = ImageDraw.Draw(img)
    title_font = font(FONT_LATIN_BOLD, 90)
    sub_font = font(FONT_CJK, 46)
    body_font = font(FONT_LATIN, 32)
    body_zh_font = font(FONT_CJK, 32)
    small_font = font(FONT_LATIN_BOLD, 28)

    draw.rounded_rectangle((50, 50, 2350, 1300), radius=44, fill="#0f172a", outline=top["color"], width=4)
    draw.rounded_rectangle((100, 100, 640, 180), radius=16, fill=top["color"])
    draw.text((130, 118), "Top News · #1 · AI Regulation", font=font(FONT_LATIN_BOLD, 34), fill="#0b1220")
    draw.text((100, 240), "Ken AI Daily", font=font(FONT_LATIN_BOLD, 84), fill="#f8fafc")
    draw.text((100, 340), "AI新聞日報 · 今日頭條", font=sub_font, fill="#cbd5e1")

    headline_lines = wrap_by_width(draw, top["headline_en"], title_font, 1280)
    y = draw_lines(draw, headline_lines, (100, 470), title_font, "#f8fafc", 10)
    y = draw_lines(draw, wrap_cjk(draw, top["headline_zh"], sub_font, 1180), (100, y + 12), sub_font, "#94a3b8", 10)

    bullets = [
        "Pre-release checks are moving closer to the model launch gate",
        "A proposed working group would pull tech executives into oversight design",
        "Policy attention is shifting from usage harms to frontier deployment control",
    ]
    bullet_y = y + 36
    for bullet in bullets:
        draw.rounded_rectangle((118, bullet_y + 12, 138, bullet_y + 32), radius=4, fill=top["color"])
        bullet_lines = wrap_by_width(draw, bullet, body_font, 980)
        bullet_y = draw_lines(draw, bullet_lines, (165, bullet_y), body_font, "#e2e8f0", 4) + 16

    draw.text((100, 1220), "Source: Reuters / New York Times report · May 4, 2026", font=font(FONT_LATIN, 24), fill="#94a3b8")

    draw.rounded_rectangle((1460, 170, 2240, 1130), radius=36, fill="#101826", outline="#334155", width=2)
    draw.rounded_rectangle((1570, 270, 2300, 360), radius=24, fill="#111827", outline=top["color"], width=4)
    draw.text((1920, 300), "Release gate", font=font(FONT_LATIN_BOLD, 34), fill="#f8fafc", anchor="mm")
    draw.rounded_rectangle((1570, 460, 2300, 770), radius=28, fill="#111827", outline=top["color"], width=4)
    draw.text((1935, 525), "Review", font=font(FONT_LATIN_BOLD, 46), fill="#f8fafc", anchor="mm")
    draw.text((1935, 595), "officials + tech execs", font=font(FONT_LATIN, 28), fill="#cbd5e1", anchor="mm")
    draw.text((1935, 650), "working group", font=font(FONT_LATIN_BOLD, 28), fill=top["color"], anchor="mm")
    draw.rounded_rectangle((1570, 870, 2300, 960), radius=24, fill="#111827", outline=top["color"], width=4)
    draw.text((1935, 900), "Models", font=font(FONT_LATIN_BOLD, 34), fill="#f8fafc", anchor="mm")
    draw.line((1935, 360, 1935, 460), fill=top["color"], width=8)
    draw.line((1935, 770, 1935, 870), fill=top["color"], width=8)
    draw.text((1935, 1028), "Ken AI Daily", font=small_font, fill="#f59e0b", anchor="mm")

    img.save(TOP_NEWS_PNG)


def write_linkedin_post() -> None:
    lines = [
        f"AI News Daily Brief — {DAY_NAME}, {DISPLAY_DATE} 🤖",
        "Ken AI Daily | AI新聞日報 | 每日雙語 AI 精選",
        "",
        "Ken AI Daily — bilingual AI news briefing covering AI models, AI agents, AI chips, AI infrastructure, AI funding, AI research, and AI regulation.",
        "",
        LINKEDIN_HOOK,
        "",
        "今日焦點 / Today’s focus:",
        LINKEDIN_FOCUS,
        "",
        "Today's top AI stories:",
        "",
    ]
    for story in STORIES:
        lines.append(f"{story['rank']}️⃣ {story['emoji']} [{story['category']}] {story['headline_en']}")
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
            "Full digest 👉 https://kenchankh97.github.io/ai-daily/",
            "",
            "#AINews #ArtificialIntelligence #AI #AIAgents #AIInfrastructure #科技新聞 #AI日報",
        ]
    )
    LINKEDIN_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_index() -> None:
    content = INDEX_PATH.read_text(encoding="utf-8")
    lead_pattern = re.compile(r"<section class=\"lead\">.*?</section>", re.S)
    ticker_pattern = re.compile(r"<section class=\"ticker\">.*?</section>", re.S)
    feed_head_pattern = re.compile(r"      <div class=\"feed-section-head\">.*?</div>", re.S)
    current_marker = '<div class="post-card post-visual" id="post-visual-20260504">'
    today_pattern = re.compile(
        rf"<div class=\"post-card post-visual\" id=\"post-visual-{DATE_ID}\">.*?(?={re.escape(current_marker)})",
        re.S,
    )

    if current_marker not in content:
        raise RuntimeError("Could not find the latest issue marker to insert before.")

    content = lead_pattern.sub(render_lead_section(), content, count=1)
    content = ticker_pattern.sub(render_ticker_section(), content, count=1)
    content = feed_head_pattern.sub(render_feed_head(), content, count=1)
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
    for marker in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "Why it matters:", "Signal to watch:", "Question for the week:", "今日焦點 / Today’s focus:"]:
        if marker not in linkedin:
            errors.append(f"missing linkedin marker: {marker}")
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
