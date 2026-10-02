"""Apple: POST https://jobs.apple.com/api/v1/search

The "format" object in the body is REQUIRED — without it the API silently
returns zero results. One search per mobile term, deduped on positionId.
The search is full-text over descriptions, so it's deliberately capped per
term; results are relevance-sorted so title matches come first.
"""
import time

from ..http import request_json
from ..models import Job, as_date, queries_for

API = "https://jobs.apple.com/api/v1/search"
JOB_URL = "https://jobs.apple.com/en-us/details/{position_id}/{slug}"
PAGE = 20
MAX_PAGES = 25


def fetch(cfg):
    jobs, seen = [], set()
    for query in queries_for(cfg):
        page, total, got = 1, None, 0
        while page <= MAX_PAGES:
            body = {"query": query, "filters": {}, "page": page, "locale": "en-us",
                    "sort": "", "format": {"longDate": "MMMM D, YYYY",
                                           "mediumDate": "MMM D, YYYY"}}
            data = request_json("POST", API, json_body=body,
                                headers={"Content-Type": "application/json"})
            res = data.get("res") or {}
            results = res.get("searchResults", [])
            if total is None:
                total = res.get("totalRecords", 0)
            if page == 1 and not results and query == "ios":
                raise RuntimeError("apple search returned no results — "
                                   "did the required 'format' body field change?")
            for j in results:
                pid = str(j.get("positionId") or j.get("id", ""))
                got += 1
                if not pid or pid in seen:
                    continue
                seen.add(pid)
                jobs.append(Job(
                    company=cfg["name"],
                    external_id=pid,
                    title=j.get("postingTitle", ""),
                    url=JOB_URL.format(position_id=j.get("positionId", ""),
                                       slug=j.get("transformedPostingTitle", "")),
                    locations=[l.get("name", "") for l in j.get("locations", []) or []],
                    posted=as_date(j.get("postDateInGMT")),
                ))
            if got >= total or not results:
                break
            page += 1
            time.sleep(0.5)
    return jobs
