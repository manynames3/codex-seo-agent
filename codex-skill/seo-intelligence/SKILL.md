---
name: seo-intelligence
description: Run a Google Search Console SEO intelligence workflow with gap analysis, competitor intelligence, weekly content planning, article drafting, and dashboard generation. Use when asked to run this seo-agent project, find keyword opportunities, inspect SEO competitors, create a content plan, write an SEO article from brand voice, or build the weekly SEO dashboard.
---

# SEO Intelligence

Use this skill to operate a Codex-ready SEO agent project.

## Project Check

Work from a project root that contains `scripts/gap_finder.py`, `scripts/competitor_intel.py`, `scripts/content_plan.py`, `scripts/build_dashboard.py`, `brand-voice.md`, and `reports/`.

If those files are missing, copy the bundled scripts from this skill's `scripts/` directory into the project root and create `reports/`, `drafts/`, and `brand-voice.md` from `references/brand-voice-example.md`.

## Session Protocol

1. Read relevant references from `references/` only as needed.
2. Read `brand-voice.md` before content planning or drafting.
3. Check `reports/` for the newest JSON files before downstream steps.
4. Never expose `.env`, `credentials.json`, or `token.pickle`.
5. Use `.venv/bin/python` if available; otherwise use `python3`.

## Workflows

Gap analysis:

```bash
python3 scripts/gap_finder.py
```

Summarize the top opportunity, highest-impression gap keywords, CTR/position issues, and recommended fixes.

Competitor intelligence:

```bash
python3 scripts/competitor_intel.py
```

Run only after a gap analysis exists. If DataForSEO credentials are absent, state that competitor output is mock fallback data and not live SERP intelligence.

Content plan:

Ask these three questions before running the script:

1. What content published last week, and did anything perform well or poorly?
2. Any new products, campaigns, or customer questions this week?
3. Anything you want to be known for that we should work into content?

Update `brand-voice.md` with relevant answers, then run:

```bash
python3 scripts/content_plan.py
```

Article drafting:

Use Codex directly. Read `brand-voice.md`, latest report JSON, and current SERP context if available. Save drafts to `drafts/[keyword-slug]-[date].md`. Before finalizing, verify the draft has customer insight, a distinctive brand position, and does not read like generic content.

Dashboard:

```bash
python3 scripts/build_dashboard.py
```

Full weekly workflow: run gap analysis, competitor intelligence, weekly check-in plus content plan, then dashboard. End with a concise consultant-style brief and paths to generated reports.
