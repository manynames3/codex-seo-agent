# Gap Finder Workflow

## Purpose

Act as an SEO analyst. When asked to run weekly gap analysis, execute `scripts/gap_finder.py` and interpret the output conversationally. Do not print raw data by default; brief the user like a consultant.

## Script

```bash
python3 scripts/gap_finder.py
```

Use `.venv/bin/python` instead of `python3` when a virtualenv exists.

## What the Script Does

1. Authenticates with Google Search Console via OAuth.
2. Pulls query-level ranking data for the past 90 days.
3. Finds gap-zone keywords ranking in positions 5-20.
4. Sorts by impression volume.
5. Assigns an action recommendation.
6. Saves:
   - `reports/gap-analysis-[date].md`
   - `reports/gap-analysis-[date].json`

## Recommendation Logic

- `NO_PAGE`: No page is capturing clicks for the query. Present it as a new article opportunity.
- `NO_INTERNAL_LINKS`: High impressions but deeper ranking. Recommend 3-5 contextual internal links from strong pages.
- `WEAK_TITLE`: Ranking is decent but CTR is weak. Recommend improving the title and meta description with a clearer outcome or proof point.
- `STRUCTURAL_ISSUE`: How-to or guide query likely needs a clearer process, table, or answer-first structure.
- `NEEDS_HUB`: Short-tail cluster likely needs a central hub page.

## Briefing Format

After the script runs, include:

- Top opportunity with keyword, impressions, position, CTR, and recommendation.
- Three quick wins to prioritize.
- Any missing credentials or Search Console data issue.
- Paths to the saved Markdown and JSON reports.

Close by asking whether the user wants competitor intelligence on the top keywords.
