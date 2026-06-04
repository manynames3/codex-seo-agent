# Brand Voice Writer Workflow

## Purpose

Act as a content strategist and writer. For content planning or drafting, read `brand-voice.md` first and use the latest reports in `reports/`.

## Content Plan Script

```bash
python3 scripts/content_plan.py
```

Use `.venv/bin/python` instead of `python3` when a virtualenv exists.

## Weekly Check-In

Always ask these questions before generating the content plan:

1. What content published last week, and did anything perform well or poorly?
2. Any new products, campaigns, or customer questions this week?
3. Anything you want to be known for that we should work into content?

Update `brand-voice.md` with relevant answers before running `scripts/content_plan.py`.

## What `content_plan.py` Does

1. Reads `brand-voice.md` and the latest gap analysis plus competitive intel JSON files.
2. Scores article opportunities using impressions, current position, and competitive threat.
3. Selects the top 4 article opportunities.
4. Generates title, target keyword, intent, and one-sentence brief.
5. Saves:
   - `reports/content-plan-[date].md`
   - `reports/content-plan-[date].json`

## Article Drafting

There is no required article-writing script. When asked to draft an article:

1. Read `brand-voice.md`.
2. Read the latest gap, competitive, and content-plan JSON files.
3. Research current SERP results when web access or a SERP API is available.
4. Draft into `drafts/[keyword-slug]-[date].md`.
5. Run the "Only You Could Write This" check before finalizing.

## Only You Could Write This Check

Before saving a final draft, verify:

- The draft includes at least one insight from the customer experience section of `brand-voice.md`.
- The draft includes at least one brand position competitors do not hold.
- The draft would not read fine on a generic content farm.

If any check fails, flag the weak section and revise it.

## Content Plan Briefing Format

After the script runs, brief:

- `P1` and `P2` priorities.
- Target keyword, estimated volume, current position, and intent.
- The one-sentence brief for each article.
- Paths to the saved Markdown and JSON reports.

Close by asking which article the user wants drafted first.
