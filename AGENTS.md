# SEO Intelligence Agent for Codex

This project is a Codex-ready SEO workflow that uses Google Search Console data to find keyword gaps, inspect competitive threats, generate a weekly content plan, and build an HTML dashboard.

## Session Start Protocol

At the start of every SEO task:

1. Read the relevant guide in `workflow-guides/`.
2. Read `brand-voice.md` before any content planning or drafting task.
3. Check `reports/` for the newest JSON outputs before running downstream workflows.
4. Verify required credentials exist before running scripts that need them.
5. Never print, commit, or modify secrets in `.env`, `credentials.json`, or `token.pickle`.

Use an existing virtualenv if present:

```bash
.venv/bin/python scripts/gap_finder.py
```

Otherwise use:

```bash
python3 scripts/gap_finder.py
```

## Available Workflows

### Gap Analysis

Trigger phrases include "Run this week's gap analysis", "What keywords should I target this week", and "Run the gap finder".

Read `workflow-guides/gap-finder.md`, then run:

```bash
python3 scripts/gap_finder.py
```

After the script runs, summarize the top opportunity, the highest-impression gap keywords, and the most actionable fixes. Do not paste raw JSON unless asked.

### Competitor Intelligence

Trigger phrases include "Run competitor intelligence", "Who's outranking me and why", and "Run competitive analysis on this week's keywords".

First confirm a recent `reports/gap-analysis-*.json` exists. Read `workflow-guides/competitor-intel.md`, then run:

```bash
python3 scripts/competitor_intel.py
```

If `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` are not configured, tell the user the competitor results are mock fallback data and should be treated as a workflow demo, not live SERP intelligence.

### Content Plan

Trigger phrases include "Generate this week's content plan" and "What should I write this week".

Before running the script, ask the weekly check-in from `workflow-guides/brand-writer.md`:

1. What content published last week, and did anything perform well or poorly?
2. Any new products, campaigns, or customer questions this week?
3. Anything you want to be known for that we should work into content?

Update `brand-voice.md` with relevant answers, then run:

```bash
python3 scripts/content_plan.py
```

Summarize the four article opportunities with priority, target keyword, current position, intent, and the one-sentence brief.

### Article Drafting

There is no required article-writing script. For "Write this week's article targeting [keyword]", use Codex directly:

1. Read `brand-voice.md`.
2. Read the latest gap, competitive, and content-plan JSON files.
3. Research the current SERP when web access or a SERP API is available.
4. Draft the article into `drafts/[keyword-slug]-[date].md`.
5. Run the "Only You Could Write This" check from `workflow-guides/brand-writer.md` before finalizing.

### Dashboard

Trigger phrases include "Build the dashboard" and "Render this week's SEO dashboard".

Run:

```bash
python3 scripts/build_dashboard.py
```

Open or link the generated `reports/dashboard-[date].html`.

### Full Weekly Workflow

For "Run the full weekly workflow":

1. Run gap analysis.
2. Run competitor intelligence.
3. Ask the content-plan weekly check-in and update `brand-voice.md`.
4. Generate the content plan.
5. Build the dashboard.
6. Brief the user on top opportunities, quick wins, content priorities, and the dashboard path.

## Output Rules

Every script writes a human-readable report and a machine-readable JSON file under `reports/`.

Use concise consultant-style summaries. Explain what changed, why it matters, and what to do next. Avoid generic SEO advice when the report includes specific keyword, position, CTR, threat, or content-plan data.
