# Ken AI Daily Automation

This repo is published by GitHub Pages at https://kenchankh97.github.io/ai-daily/.

## Daily Job Contract

The scheduled Codex job runs every day at 08:00 Hong Kong time.

Each run should:

1. Find the top 6 AI stories published or materially updated in the last 24 hours.
2. Prefer official sources, primary research, regulator/policy sources, and major reputable media.
3. Update `index.html` in the existing editorial style, with English first and Traditional Chinese second.
4. Generate a daily infographic PNG named `ai-daily-YYYYMMDD.png`.
5. Keep the visual style consistent with existing `ai-daily-*.png` images.
6. Create `linkedin-post.txt` with the bilingual LinkedIn post copy.
7. Validate the site locally enough to catch broken HTML, missing images, and missing bilingual fields.
8. Commit and push changes to `main`.
9. Publish the LinkedIn post with:

   ```powershell
   python scripts\linkedin_post_ugc.py --text-file linkedin-post.txt --image ai-daily-YYYYMMDD.png --title "Ken AI Daily YYYY-MM-DD"
   ```

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

Use this structure:

```text
Ken AI Daily — Tuesday, April 28, 2026
Ken AI 日報 | 每日雙語 AI 精選

Today's top stories:

1️⃣ English headline
Traditional Chinese headline

...

Full digest https://kenchankh97.github.io/ai-daily/

#AINews #KenAIDaily #ArtificialIntelligence #科技新聞 #AI日報
```
