"""Eightfold-hosted career sites (Netflix, Qualcomm, ...).

GET https://{host}/api/apply/v2/jobs?domain={domain}&query={q}&num=100&start=N
One search per mobile term, deduped on position id.
"""
import time

from ..http import request_json
from ..models import Job, as_date, queries_for

MAX_PAGES = 30


def fetch(cfg):
    host = cfg["host"]          # e.g. "explore.jobs.netflix.net"
    domain = cfg["domain"]      # e.g. "netflix.com"
    api = "https://{}/api/apply/v2/jobs".format(host)

    jobs, seen = [], set()
    for query in queries_for(cfg):
        start = 0
        for _ in range(MAX_PAGES):
            params = {"domain": domain, "query": query, "num": 100, "start": start,
                      "sort_by": "relevance"}
            data = request_json("GET", api, params=params)
            positions = data.get("positions", [])
            for p in positions:
                pid = str(p.get("id") or p.get("ats_job_id", ""))
                if not pid or pid in seen:
                    continue
                seen.add(pid)
                url = p.get("canonicalPositionUrl") or \
                    "https://{}/careers/job/{}".format(host, pid)
                locations = p.get("locations") or [p.get("location", "")]
                jobs.append(Job(
                    company=cfg["name"],
                    external_id=pid,
                    title=p.get("name", ""),
                    url=url,
                    locations=[str(l) for l in locations],
                    posted=as_date(p.get("t_create")),
                ))
            start += len(positions)
            if not positions or start >= data.get("count", 0):
                break
            time.sleep(0.5)
    return jobs
