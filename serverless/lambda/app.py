import base64
import datetime as dt
import hashlib
import html
import json
import os
import time
import urllib.parse
import uuid

import boto3
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


PROJECT_NAME = os.getenv("PROJECT_NAME", "codex-seo-agent")
REPORTS_BUCKET = os.environ["REPORTS_BUCKET"]
ADMIN_TOKEN_PARAM = os.getenv("ADMIN_TOKEN_PARAM", f"/{PROJECT_NAME}/admin-token")
GOOGLE_CLIENT_SECRET_PARAM = os.getenv(
    "GOOGLE_CLIENT_SECRET_PARAM", f"/{PROJECT_NAME}/google-client-secret-json"
)
GOOGLE_TOKEN_PARAM = os.getenv("GOOGLE_TOKEN_PARAM", f"/{PROJECT_NAME}/google-token-json")
DATAFORSEO_LOGIN_PARAM = os.getenv("DATAFORSEO_LOGIN_PARAM", f"/{PROJECT_NAME}/dataforseo-login")
DATAFORSEO_PASSWORD_PARAM = os.getenv(
    "DATAFORSEO_PASSWORD_PARAM", f"/{PROJECT_NAME}/dataforseo-password"
)

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

ssm = boto3.client("ssm")
s3 = boto3.client("s3")


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath") or "/"

    if method == "OPTIONS":
        return response(204, "")

    try:
        if path == "/health":
            return response(200, {"ok": True, "project": PROJECT_NAME})
        if path == "/auth/google/start" and method == "GET":
            return start_google_oauth(event)
        if path == "/auth/google/callback" and method == "GET":
            return finish_google_oauth(event)
        if path == "/api/run" and method == "POST":
            require_admin(event)
            return run_workflow(event)
        if path == "/api/reports" and method == "GET":
            require_admin(event)
            return list_reports()
        return response(404, {"error": "Not found", "path": path})
    except PermissionError as exc:
        return response(401, {"error": str(exc)})
    except Exception as exc:
        print(f"ERROR {type(exc).__name__}: {exc}")
        return response(500, {"error": str(exc), "type": type(exc).__name__})


def response(status, body, headers=None):
    merged_headers = {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET,POST,OPTIONS",
        "access-control-allow-headers": "authorization,content-type",
        "cache-control": "no-store",
    }
    if headers:
        merged_headers.update(headers)
    if isinstance(body, (dict, list)):
        merged_headers["content-type"] = "application/json"
        body = json.dumps(body, indent=2)
    elif not isinstance(body, str):
        body = str(body)
    return {"statusCode": status, "headers": merged_headers, "body": body}


def html_response(status, markup):
    return response(status, markup, {"content-type": "text/html; charset=utf-8"})


def redirect(url):
    return {"statusCode": 302, "headers": {"location": url}, "body": ""}


def get_query(event):
    return event.get("queryStringParameters") or {}


def get_body(event):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body)


def get_param(name, decrypt=True, required=True):
    try:
        return ssm.get_parameter(Name=name, WithDecryption=decrypt)["Parameter"]["Value"]
    except ssm.exceptions.ParameterNotFound:
        if required:
            raise RuntimeError(f"Missing SSM parameter: {name}")
        return None


def put_param(name, value, secure=True):
    ssm.put_parameter(
        Name=name,
        Value=value,
        Type="SecureString" if secure else "String",
        Overwrite=True,
    )


def require_admin(event):
    expected = get_param(ADMIN_TOKEN_PARAM)
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    auth = headers.get("authorization", "")
    supplied = ""
    if auth.lower().startswith("bearer "):
        supplied = auth.split(" ", 1)[1].strip()
    elif get_query(event).get("token"):
        supplied = get_query(event)["token"]
    if not supplied or not constant_time_equal(supplied, expected):
        raise PermissionError("Invalid or missing admin token")


def constant_time_equal(left, right):
    return hashlib.sha256(left.encode()).digest() == hashlib.sha256(right.encode()).digest()


def public_base_url(event):
    headers = event.get("headers") or {}
    host = headers.get("host") or headers.get("Host")
    proto = headers.get("x-forwarded-proto") or "https"
    return f"{proto}://{host}"


def load_google_client_config():
    raw = get_param(GOOGLE_CLIENT_SECRET_PARAM)
    config = json.loads(raw)
    if "web" not in config:
        raise RuntimeError("Google OAuth client JSON must be a Web application client with a 'web' key")
    return config


def start_google_oauth(event):
    require_admin(event)
    query = get_query(event)
    site_url = query.get("site_url") or ""
    callback_url = f"{public_base_url(event)}/auth/google/callback"
    state = json.dumps(
        {
            "nonce": str(uuid.uuid4()),
            "site_url": site_url,
            "created": int(time.time()),
        },
        separators=(",", ":"),
    )
    flow = Flow.from_client_config(load_google_client_config(), scopes=SCOPES)
    flow.redirect_uri = callback_url
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=base64.urlsafe_b64encode(state.encode()).decode(),
    )
    return redirect(auth_url)


def finish_google_oauth(event):
    query = get_query(event)
    encoded_state = query.get("state", "")
    if not encoded_state:
        return html_response(400, page("Missing State", "Google did not return an OAuth state."))
    try:
        state = json.loads(base64.urlsafe_b64decode(encoded_state.encode()).decode())
    except Exception:
        return html_response(400, page("Bad State", "OAuth state could not be decoded."))
    if int(time.time()) - int(state.get("created", 0)) > 900:
        return html_response(400, page("Expired State", "OAuth state expired. Start the connection again."))

    callback_url = f"{public_base_url(event)}/auth/google/callback"
    full_url = f"{callback_url}?{event.get('rawQueryString', '')}"
    flow = Flow.from_client_config(load_google_client_config(), scopes=SCOPES)
    flow.redirect_uri = callback_url
    flow.fetch_token(authorization_response=full_url)
    creds = flow.credentials
    put_param(GOOGLE_TOKEN_PARAM, creds.to_json())

    site = state.get("site_url") or "your Search Console property"
    return html_response(
        200,
        page(
            "Google Search Console Connected",
            f"Connected successfully. You can close this tab and run reports for {html.escape(site)}.",
        ),
    )


def page(title, message):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:#0b0f14; color:#eef6fb; font-family:system-ui,sans-serif; }}
    main {{ width:min(680px, calc(100% - 32px)); background:#111821; border:1px solid #243241; border-radius:8px; padding:28px; }}
    p {{ color:#92a5b4; line-height:1.6; }}
  </style>
</head>
<body><main><h1>{html.escape(title)}</h1><p>{message}</p></main></body>
</html>"""


def load_credentials():
    raw = get_param(GOOGLE_TOKEN_PARAM)
    creds = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        put_param(GOOGLE_TOKEN_PARAM, creds.to_json())
    if not creds.valid:
        raise RuntimeError("Stored Google credentials are invalid. Reconnect Google Search Console.")
    return creds


def fetch_gsc_data(site_url, days=90):
    service = build("searchconsole", "v1", credentials=load_credentials(), cache_discovery=False)
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=days)
    body = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": ["query"],
        "rowLimit": 1000,
        "startRow": 0,
    }
    data = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return data.get("rows", [])


def generate_recommendation(keyword, position, impressions, ctr):
    keyword_lower = keyword.lower()
    if ctr == 0.0:
        return (
            "NO_PAGE",
            "New article opportunity. No page is capturing clicks for this query. A dedicated post targeting this exact phrase could land page 1 within 30-60 days.",
        )
    if position <= 8 and ctr < 0.03:
        return (
            "WEAK_TITLE",
            "Update the title and meta description. You're ranking well but not getting clicks. Add a specific outcome or number to the title.",
        )
    if position > 12 and impressions > 500:
        return (
            "NO_INTERNAL_LINKS",
            "Add internal links. High impressions but deep ranking suggests the page needs more internal authority. Add 3-5 links from high-traffic posts.",
        )
    if any(word in keyword_lower for word in ["how", "guide", "tutorial", "steps"]):
        return (
            "STRUCTURAL_ISSUE",
            "Restructure the post. How-to queries reward numbered steps and a clear answer in the first paragraph.",
        )
    if len(keyword.split()) <= 2:
        return (
            "NEEDS_HUB",
            "Add a hub page. Short-tail keyword suggests multiple variations need one central article consolidating authority.",
        )
    return (
        "WEAK_TITLE",
        "Improve content depth. Review the top ranking pages and add the missing section, comparison table, or FAQ that would help this page move up.",
    )


def run_gap_analysis(site_url):
    rows = fetch_gsc_data(site_url)
    gap_zone = []
    for row in rows:
        position = row.get("position", 0)
        impressions = row.get("impressions", 0)
        clicks = row.get("clicks", 0)
        ctr = row.get("ctr", 0)
        query = row["keys"][0]
        if 5 <= position <= 20 and impressions >= 1:
            rec_type, rec = generate_recommendation(query, position, impressions, ctr)
            gap_zone.append(
                {
                    "keyword": query,
                    "impressions": int(impressions),
                    "position": round(position, 1),
                    "clicks": int(clicks),
                    "ctr": round(ctr * 100, 1),
                    "rec_type": rec_type,
                    "recommendation": rec,
                }
            )
    gap_zone.sort(key=lambda x: x["impressions"], reverse=True)
    top = gap_zone[:10]
    return {
        "date": dt.date.today().isoformat(),
        "site_url": site_url,
        "total_gap_keywords": len(gap_zone),
        "top_opportunity": top[0] if top else None,
        "keywords": top,
        "kpis": {
            "total_impressions": sum(r.get("impressions", 0) for r in rows),
            "gap_zone_count": len(gap_zone),
            "avg_position": round(sum(r.get("position", 0) for r in rows) / len(rows), 1) if rows else 0,
            "total_clicks": sum(r.get("clicks", 0) for r in rows),
        },
    }


def get_optional_dataforseo():
    login = get_param(DATAFORSEO_LOGIN_PARAM, required=False)
    password = get_param(DATAFORSEO_PASSWORD_PARAM, required=False)
    return login, password


def search_google(query, num_results=3):
    login, password = get_optional_dataforseo()
    if not login or not password:
        return [
            {
                "domain": f"mock-competitor-{i + 1}.com",
                "title": f"Top result {i + 1} for {query}",
                "url": f"https://mock-competitor-{i + 1}.com/{query.replace(' ', '-')}",
                "rank": i + 1,
                "mock": True,
            }
            for i in range(num_results)
        ]
    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    payload = [{"keyword": query, "location_code": 2840, "language_code": "en", "depth": 10}]
    data = requests.post(url, auth=(login, password), json=payload, timeout=30).json()
    results = []
    items = data.get("tasks", [{}])[0].get("result", [{}])[0].get("items", [])
    for item in items:
        if item.get("type") == "organic":
            results.append(
                {
                    "url": item.get("url", ""),
                    "domain": item.get("domain", ""),
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "rank": item.get("rank_absolute", 0),
                    "mock": False,
                }
            )
        if len(results) >= num_results:
            break
    return results


def analyze_competitor(competitor, keyword):
    domain = competitor.get("domain", "")
    title = competitor.get("title", "")
    high_authority = [
        "shopify.com",
        "hubspot.com",
        "semrush.com",
        "ahrefs.com",
        "moz.com",
        "backlinko",
        "searchenginejournal",
        "zapier.com",
    ]
    is_high_authority = any(d in domain.lower() for d in high_authority)
    has_year = str(dt.date.today().year) in title or str(dt.date.today().year - 1) in title
    has_comparison = any(w in title.lower() for w in ["vs", "versus", "compare", "best", "top"])
    has_guide = any(w in title.lower() for w in ["guide", "tutorial", "how to", "steps"])
    is_brand_result = keyword.lower().split()[0] in domain.lower() if keyword else False
    if is_brand_result:
        return "HIGH", f"Ranking for its own brand term. Reframe with an alternatives or niche angle instead."
    if is_high_authority:
        return "HIGH", "Massive domain authority. Hard to displace with content alone; target a narrower subtopic."
    if has_year:
        return "MEDIUM", "Uses a current-year freshness signal. Add a current-year section and update the title."
    if has_comparison:
        return "MEDIUM", "Comparison/list format is likely matching SERP intent. Add a structured comparison table."
    if has_guide:
        return "MEDIUM", "Guide format likely wins on depth and structure. Match depth and build internal links."
    return "LOW", "Likely thin or accidental ranking. Beatable with one focused, well-structured post."


def run_competitor_intel(gap_data):
    results = []
    quick_wins = []
    avoid_list = []
    mock_mode = False
    keywords = [kw["keyword"] for kw in gap_data.get("keywords", [])[:8]]
    for keyword in keywords:
        competitors = search_google(keyword, 3)
        keyword_results = []
        for comp in competitors:
            mock_mode = mock_mode or comp.get("mock", False)
            threat, reason = analyze_competitor(comp, keyword)
            entry = {
                "keyword": keyword,
                "competitor": comp.get("domain", "unknown"),
                "url": comp.get("url", ""),
                "threat": threat,
                "reason": reason,
                "mock": comp.get("mock", False),
            }
            keyword_results.append(entry)
            results.append(entry)
            if threat == "LOW":
                quick_wins.append(entry)
            if threat == "HIGH":
                avoid_list.append({"keyword": keyword, "competitor": comp.get("domain"), "reason": reason})
        time.sleep(0.25)
    return {
        "date": dt.date.today().isoformat(),
        "keywords_analyzed": len(keywords),
        "results": results,
        "quick_wins": quick_wins[:3],
        "avoid_list": avoid_list[:3],
        "mock_mode": mock_mode,
    }


def classify_intent(keyword):
    kw = keyword.lower()
    if any(w in kw for w in ["how to", "how do", "tutorial", "guide", "steps", "setup"]):
        return "How-To"
    if any(w in kw for w in ["best", "top", "vs", "versus", "compare", "alternative", "review"]):
        return "Commercial Investigation"
    if any(w in kw for w in ["buy", "price", "cost", "cheap", "discount", "deal"]):
        return "Transactional"
    return "Informational"


def generate_title(keyword, intent):
    year = dt.date.today().year
    kw_title = keyword.title()
    if intent == "How-To":
        return f"How to {kw_title}: A Step-by-Step Guide ({year})"
    if intent == "Commercial Investigation":
        return f"Best {kw_title}: Honest Comparison ({year})"
    if intent == "Transactional":
        return f"{kw_title}: What to Look For Before You Buy ({year})"
    return f"{kw_title}: The Complete Guide ({year})"


def generate_brief(intent):
    if intent == "How-To":
        return "Lead with the outcome, show a real workflow, and make the steps easy to scan."
    if intent == "Commercial Investigation":
        return "Use a neutral comparison with a table above the fold and a clear point of view."
    if intent == "Transactional":
        return "Give buying criteria, tradeoffs, and a clear recommendation."
    return "Build a definitive resource that covers the topic fully and links to supporting posts."


def run_content_plan(gap_data, comp_data):
    threat_lookup = {}
    for result in comp_data.get("results", []):
        threat_lookup.setdefault(result["keyword"], result["threat"])
    scored = []
    for kw_data in gap_data.get("keywords", [])[:8]:
        keyword = kw_data["keyword"]
        impressions = kw_data["impressions"]
        position = kw_data["position"]
        threat = threat_lookup.get(keyword, "MEDIUM")
        threat_score = {"LOW": 3, "MEDIUM": 2, "HIGH": 0}.get(threat, 1)
        position_score = max(0, 20 - position)
        impression_score = min(impressions / 100, 10)
        if threat == "HIGH":
            keyword = f"{keyword} for niche buyers"
        scored.append(
            {
                "keyword": keyword,
                "original_keyword": kw_data["keyword"],
                "impressions": impressions,
                "position": position,
                "ctr": kw_data["ctr"],
                "threat": threat,
                "score": threat_score * 3 + position_score + impression_score,
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    articles = []
    for i, item in enumerate(scored[:4]):
        intent = classify_intent(item["keyword"])
        articles.append(
            {
                "priority": "P1" if i < 2 else "P2",
                "title": generate_title(item["keyword"], intent),
                "keyword": item["keyword"],
                "estimated_volume": item["impressions"],
                "current_position": item["position"],
                "intent": intent,
                "brief": generate_brief(intent),
                "threat": item["threat"],
            }
        )
    return {"date": dt.date.today().isoformat(), "articles": articles}


def markdown_gap(data):
    lines = [
        f"# Gap Analysis - {data['site_url']}",
        f"**Date:** {data['date']} | **Window:** 90 days",
        "",
        "## Summary",
        f"- Total gap-zone keywords: {data['total_gap_keywords']}",
        f"- Total impressions: {data['kpis']['total_impressions']:,}",
        f"- Average position: {data['kpis']['avg_position']}",
        f"- Total clicks: {data['kpis']['total_clicks']:,}",
        "",
    ]
    if data.get("top_opportunity"):
        top = data["top_opportunity"]
        lines += [
            "## Top Opportunity",
            f"**{top['keyword']}** - {top['impressions']:,} impressions, position {top['position']}, {top['ctr']}% CTR",
            f"> {top['recommendation']}",
            "",
        ]
    lines.append("## Keyword Opportunities")
    for kw in data.get("keywords", []):
        lines += [
            f"### {kw['keyword']}",
            f"- Impressions: {kw['impressions']:,}",
            f"- Position: {kw['position']}",
            f"- CTR: {kw['ctr']}%",
            f"- Recommendation: {kw['recommendation']}",
            "",
        ]
    return "\n".join(lines)


def markdown_comp(data):
    lines = ["# Competitive Intelligence", f"**Date:** {data['date']}", ""]
    if data.get("mock_mode"):
        lines += ["> DataForSEO is not configured. Results use mock competitors for workflow demonstration.", ""]
    lines += ["| Keyword | Competitor | Threat | Why They Win |", "|---|---|---|---|"]
    for row in data.get("results", []):
        lines.append(f"| {row['keyword']} | {row['competitor']} | {row['threat']} | {row['reason']} |")
    return "\n".join(lines)


def markdown_plan(data):
    lines = ["# Weekly Content Plan", f"**Date:** {data['date']}", ""]
    for article in data.get("articles", []):
        lines += [
            f"## {article['priority']} - {article['title']}",
            f"- Target keyword: {article['keyword']}",
            f"- Estimated volume: {article['estimated_volume']:,}",
            f"- Current position: {article['current_position']}",
            f"- Intent: {article['intent']}",
            f"- Threat: {article['threat']}",
            f"- Brief: {article['brief']}",
            "",
        ]
    return "\n".join(lines)


def build_dashboard_html(gap, comp, plan):
    cards = []
    for kw in gap.get("keywords", [])[:6]:
        cards.append(
            f"<article><h3>{html.escape(kw['keyword'])}</h3><p>{kw['impressions']:,} impressions | Position {kw['position']} | CTR {kw['ctr']}%</p><small>{html.escape(kw['recommendation'])}</small></article>"
        )
    articles = []
    for item in plan.get("articles", []):
        articles.append(
            f"<article><b>{html.escape(item['priority'])}</b><h3>{html.escape(item['title'])}</h3><p>{html.escape(item['keyword'])} | {html.escape(item['intent'])}</p><small>{html.escape(item['brief'])}</small></article>"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEO Dashboard - {html.escape(gap.get('site_url', 'site'))}</title>
<style>body{{margin:0;background:#0b0f14;color:#eef6fb;font-family:system-ui,sans-serif}}main{{width:min(1120px,calc(100% - 32px));margin:0 auto;padding:32px}}section{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}article{{background:#111821;border:1px solid #243241;border-radius:8px;padding:16px}}p,small{{color:#92a5b4}}</style></head>
<body><main><h1>SEO Dashboard</h1><p>{html.escape(gap.get('site_url',''))} | {html.escape(gap.get('date',''))}</p>
<h2>Keyword Opportunities</h2><section>{''.join(cards)}</section>
<h2>Content Plan</h2><section>{''.join(articles)}</section></main></body></html>"""


def upload_report(key, body, content_type):
    s3.put_object(Bucket=REPORTS_BUCKET, Key=key, Body=body.encode("utf-8"), ContentType=content_type)
    return f"s3://{REPORTS_BUCKET}/{key}"


def presigned_url(key):
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": REPORTS_BUCKET, "Key": key},
        ExpiresIn=3600,
    )


def run_workflow(event):
    body = get_body(event)
    site_url = body.get("site_url")
    if not site_url:
        raise RuntimeError("site_url is required. Example: sc-domain:example.com")
    today = dt.date.today().isoformat()
    prefix = f"reports/{today}/"

    gap = run_gap_analysis(site_url)
    comp = run_competitor_intel(gap)
    plan = run_content_plan(gap, comp)
    dashboard = build_dashboard_html(gap, comp, plan)

    outputs = {
        "gap_json": upload_report(f"{prefix}gap-analysis.json", json.dumps(gap, indent=2), "application/json"),
        "gap_md": upload_report(f"{prefix}gap-analysis.md", markdown_gap(gap), "text/markdown"),
        "competitive_json": upload_report(f"{prefix}competitive.json", json.dumps(comp, indent=2), "application/json"),
        "competitive_md": upload_report(f"{prefix}competitive.md", markdown_comp(comp), "text/markdown"),
        "content_plan_json": upload_report(f"{prefix}content-plan.json", json.dumps(plan, indent=2), "application/json"),
        "content_plan_md": upload_report(f"{prefix}content-plan.md", markdown_plan(plan), "text/markdown"),
        "dashboard_html": upload_report(f"{prefix}dashboard.html", dashboard, "text/html"),
    }
    links = {
        "dashboard": presigned_url(f"{prefix}dashboard.html"),
        "gap_report": presigned_url(f"{prefix}gap-analysis.md"),
        "competitive_report": presigned_url(f"{prefix}competitive.md"),
        "content_plan": presigned_url(f"{prefix}content-plan.md"),
    }
    return response(
        200,
        {
            "ok": True,
            "site_url": site_url,
            "date": today,
            "gap": gap,
            "competitive": comp,
            "content_plan": plan,
            "outputs": outputs,
            "links": links,
        },
    )


def list_reports():
    resp = s3.list_objects_v2(Bucket=REPORTS_BUCKET, Prefix="reports/", MaxKeys=100)
    items = []
    for obj in resp.get("Contents", []):
        key = obj["Key"]
        items.append(
            {
                "key": key,
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
                "url": presigned_url(key),
            }
        )
    items.sort(key=lambda x: x["last_modified"], reverse=True)
    return response(200, {"reports": items})
