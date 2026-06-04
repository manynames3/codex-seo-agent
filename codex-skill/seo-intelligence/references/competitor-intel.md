# Competitor Intelligence Workflow

## Purpose

Act as a competitive SEO analyst. When asked to run competitor intelligence, execute `scripts/competitor_intel.py` and present specific, actionable findings.

## Script

```bash
python3 scripts/competitor_intel.py
```

Use `.venv/bin/python` instead of `python3` when a virtualenv exists.

## Preconditions

Run only after a recent `reports/gap-analysis-*.json` exists. The script reads the latest gap analysis and analyzes the top keywords.

If `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` are configured, the script uses DataForSEO for live organic SERP results. If they are missing, the script uses mock fallback competitors. In fallback mode, clearly label the output as a workflow demo, not live competitor intelligence.

## What the Script Does

1. Reads the latest gap analysis JSON.
2. Takes the top 5-10 gap-zone keywords.
3. Fetches or mocks the top 3 ranking pages for each keyword.
4. Analyzes competitor title, domain signals, SERP format, and likely content structure.
5. Assigns threat level: `HIGH`, `MEDIUM`, or `LOW`.
6. Saves:
   - `reports/competitive-[date].md`
   - `reports/competitive-[date].json`

## Threat Criteria

- `HIGH`: Hard to displace. Usually a brand term, massive authority site, or structural advantage that takes months to match.
- `MEDIUM`: Beatable in 30-60 days with a focused update, stronger structure, or new piece.
- `LOW`: Thin, weak, or accidental ranking. One focused article may outrank it.

## Briefing Format

After the script runs, include:

- Who is beating the user and why.
- Low-threat quick wins.
- High-threat keywords to avoid or reframe.
- Specific fixes, not generic SEO advice.
- Paths to the saved Markdown and JSON reports.

Close by asking whether the user wants a content plan based on the findings.
