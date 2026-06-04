# Codex SEO Agent

Codex-ready adaptation of `mikefutia/seo-agent`.

This project uses Google Search Console data to:

- Find keyword opportunities in positions 5-20.
- Analyze competitors for top gap keywords.
- Generate a weekly content plan.
- Build an HTML SEO dashboard.

## What Changed for Codex

- Added `AGENTS.md` as the project brain Codex reads in this repo.
- Converted Claude-oriented skill notes into `workflow-guides/`.
- Added an optional installable Codex skill at `codex-skill/seo-intelligence`.
- Genericized `brand-voice.md` and `.env.example`.
- Moved dated upstream sample reports into `examples/sample-reports/` so live runs start from a clean `reports/` directory.
- Updated dashboard output from "Powered by Claude Code" to "Powered by Codex".
- Removed the missing `write_article.py` requirement; article drafting is handled directly by Codex and saved to `drafts/`.

## Start Here

1. Follow `SETUP.md`.
2. Fill in `brand-voice.md`.
3. Open Codex in this folder.
4. Say: `Run the full weekly workflow`.

Generated reports land in `reports/`; article drafts land in `drafts/`.

## Cloudflare Pages

The deployable static front end lives in `public/`.

```bash
wrangler pages deploy public --project-name codex-seo-agent --branch main
```

The deployed page is a static project front door. Google Search Console analysis runs locally in Codex so OAuth credentials stay out of Cloudflare Pages.
