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
6. Create `linkedin-post.txt` with the bilingual LinkedIn post copy in the exact style below.
7. Validate the site locally enough to catch broken HTML, missing images, missing bilingual fields, malformed Unicode, and missing LinkedIn story lines.
8. Commit and push changes to `main`.
9. Publish the LinkedIn post with the UGC helper:

   ```powershell
   python scripts\linkedin_post_ugc.py --text-file linkedin-post.txt --image ai-daily-YYYYMMDD.png --title "Ken AI Daily YYYY-MM-DD"
   ```

Do not use `scripts\linkedin_post.py` for the newsletter image post. The `/rest/posts` flow returned `201 Created` but rendered only the first visible commentary lines in LinkedIn. Use `scripts\linkedin_post_ugc.py`, which publishes through `shareCommentary.text`.

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
Ken AI Daily ? Tuesday, April 28, 2026 ??
Ken AI ?? | ???? AI ??

???? / Today?s focus:
One sharp editorial sentence summarizing the theme connecting today's six stories.

Today's top stories:

1?? ?? English headline
   Traditional Chinese headline

2?? ?? English headline
   Traditional Chinese headline

...

Why it matters:
One to two concise sentences explaining the strategic significance for AI, business, product, infrastructure, or policy.

Full digest ?? https://kenchankh97.github.io/ai-daily/

#AINews #KenAIDaily #ArtificialIntelligence #AI #???? #AI??
```

## Validation Checklist

Before publishing:

- `linkedin-post.txt` contains `1️⃣` through `6️⃣`.
- Each English headline has an indented Traditional Chinese headline below it.
- The post includes `???? / Today?s focus:` and `Why it matters:` sections.
- There is one blank line between each numbered story pair.
- There are no replacement artifacts such as question marks where Chinese or emoji should appear.
- Today's PNG exists, has meaningful file size, and renders readable Chinese text.
- Today's `index.html` block contains six story cards and references today's PNG.
- All six story source links return 200 or have a clearly justified accessible replacement source.

After publishing:

- If LinkedIn renders a malformed post, publish the corrected post first, then delete the bad post.
- Record the final LinkedIn share URN in the run summary.
