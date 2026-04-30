# Ken AI Daily Automation

This repo is published by GitHub Pages at https://kenchankh97.github.io/ai-daily/.

## Daily Job Contract

The scheduled Codex job runs every day at 08:00 Hong Kong time.

Each run should:

1. Find the top 6 AI stories published or materially updated in the last 24 hours.
2. Prefer official sources, primary research, regulator/policy sources, and major reputable media.
3. Update `index.html` in the existing editorial style, with English first and Traditional Chinese second.
4. Generate the site daily summary PNG named `ai-daily-YYYYMMDD.png`.
5. Generate a separate LinkedIn attachment PNG named `ai-daily-YYYYMMDD-top-news.png` based on the #1 ranked story's infographic, not the daily summary image.
6. Keep both PNGs at `2400x1350` so site display and LinkedIn compression remain sharp. Reference `ai-daily-YYYYMMDD.png` with the same dimensions in `index.html`.
7. Create `linkedin-post.txt` with the bilingual LinkedIn post copy in the exact style below.
8. Validate the site locally enough to catch broken HTML, missing images, missing bilingual fields, malformed Unicode, missing LinkedIn story lines, soft image output, wrong LinkedIn attachment, and repetitive infographics.
9. Commit and push changes to `main`.
10. Publish the LinkedIn post with the UGC helper using the top-news PNG:

   ```powershell
   python scripts\linkedin_post_ugc.py --text-file linkedin-post.txt --image ai-daily-YYYYMMDD-top-news.png --title "Ken AI Daily YYYY-MM-DD"
   ```

Do not use `scripts\linkedin_post.py` for the newsletter image post. The `/rest/posts` flow returned `201 Created` but rendered only the first visible commentary lines in LinkedIn. Use `scripts\linkedin_post_ugc.py`, which publishes through `shareCommentary.text`.

## Visual Quality Requirements

- Generate the site summary PNG at `2400x1350` with large type, high contrast, and readable Traditional Chinese. Avoid `1200x675` as the source image because LinkedIn compression can make it look soft.
- Generate the LinkedIn attachment as a separate `ai-daily-YYYYMMDD-top-news.png` image at `2400x1350`. It should feature the #1 ranked story's headline, Traditional Chinese headline, source, category, and the same visual metaphor as that story's inline infographic. Do not attach the daily summary image to LinkedIn.
- The daily summary image under `The Brief` must render at its natural 16:9 ratio. Keep or add the CSS guard for `.post-visual img`: `display:block`, `width:100%`, `height:auto !important`, `aspect-ratio:16/9`, and `object-fit:contain`. Do not rely only on the image `width` and `height` attributes.
- Use a known CJK font such as `C:/Windows/Fonts/msjh.ttc` or `C:/Windows/Fonts/msyh.ttc` when rendering with Pillow.
- Guard against Windows console encoding damage. If a generation script is sent through PowerShell, use UTF-8 files or Unicode escapes for Chinese and emoji, then validate that the PNG and HTML do not contain replacement artifacts where Chinese or emoji should appear.
- The six inline SVG infographic sections should not all reuse the same bar-card template. Vary the visual metaphor by story type, for example: agent stack, connector grid, policy matrix, cyber alert, workflow map, impact ladder, market map, compute pipeline, regulation timeline, or robotics flow.
- Validate the PNG visually before publishing and verify `index.html` uses `width="2400" height="1350"` for today's image.
- Before commit and especially before LinkedIn publishing, verify the live/site image slot is not vertically stretched: the displayed Brief image ratio should be close to `1.7778` (`16 / 9`). If browser tooling is unavailable, at minimum verify the `.post-visual img` CSS guard is present and the PNG dimensions are exactly `2400x1350`.

## Recurring Failure Lessons

- Do not stop after generating files. The run is incomplete until the commit is pushed and the LinkedIn UGC helper returns a share URN, or a clear blocker is reported.
- If `git add` fails with `Unable to create .git/index.lock: Permission denied`, check for `.git/index.lock`, verify `git status --short`, and retry after the runtime permissions are available. Do not run LinkedIn publishing until the site commit is pushed.
- A successful LinkedIn API response is not enough if the site is visually broken or the wrong image was attached. Check the site summary image, the Brief image presentation in `index.html`, the top-news LinkedIn attachment, and the LinkedIn post shape before declaring success.

## Local Secrets

Secrets live in `.env`, which is ignored by git. Required keys:

```env
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_AUTHOR_URN=
LINKEDIN_API_VERSION=202604
```

## LinkedIn Copy Style

Use this structure, including one blank line between each numbered story pair:

```text
Ken AI Daily — Tuesday, April 28, 2026 🤖
Ken AI 日報 | 每日雙語 AI 精選

AI is no longer just a model race — it is becoming a race for chips, energy, distribution, and regulation.

今日焦點 / Today’s focus:
One sharp editorial sentence summarizing the theme connecting today's six stories.

Today's top stories:

1️⃣ 🤖 [Models] English headline
   Traditional Chinese headline

2️⃣ 💰 [Funding] English headline
   Traditional Chinese headline

...

Why it matters:
Audience-focused insight explaining what the stories mean for business leaders, builders, investors, policy watchers, or AI adopters.

Signal to watch:
One forward-looking takeaway about what to monitor next.

Question for the week:
One short engagement question that invites comments without sounding clickbait.

Full digest 👉 https://kenchankh97.github.io/ai-daily/

#AINews #KenAIDaily #ArtificialIntelligence #AI #科技新聞 #AI日報
```

## Validation Checklist

Before publishing:

- `linkedin-post.txt` contains `1️⃣` through `6️⃣`.
- Each English headline has an indented Traditional Chinese headline below it.
- The post includes `今日焦點 / Today’s focus:` and `Why it matters:` sections.
- There is one blank line between each numbered story pair.
- There are no replacement artifacts such as question marks where Chinese or emoji should appear.
- Today's site summary PNG exists, is `2400x1350`, has meaningful file size, and renders readable Chinese text.
- Today's LinkedIn top-news PNG exists as `ai-daily-YYYYMMDD-top-news.png`, is `2400x1350`, has meaningful file size, renders readable Chinese text, and is visually focused on story #1 rather than the six-story summary.
- Today's `index.html` block contains six story cards and references today's PNG.
- Today's Brief summary image has the `.post-visual img` aspect-ratio guard and cannot stretch vertically.
- Today's `index.html` block contains six visually varied inline SVG infographic sections.
- All six story source links return 200 or have a clearly justified accessible replacement source.

After publishing:

- If LinkedIn renders a malformed or low-quality post, publish the corrected post first, then delete the bad post after the corrected post succeeds.
- Record the final LinkedIn share URN in the run summary.
