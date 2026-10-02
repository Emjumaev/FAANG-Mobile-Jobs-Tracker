"""Amazon: https://www.amazon.jobs/en/search.json

One full-text pass per mobile search term, deduped on the iCIMS id.
"""
import time

from ..http import request_json
from ..models import Job, as_date, queries_for

API = "https://www.amazon.jobs/en/search.json"
PAGE = 100
MAX_PAGES = 10


def fetch(cfg):
    jobs, seen = [], set()
    for query in queries_for(cfg):
        offset = 0
        for _ in range(MAX_PAGES):
            params = {"base_query": query, "result_limit": PAGE, "offset": offset}
            data = request_json("GET", API, params=params)
            batch = data.get("jobs", [])
            for j in batch:
                jid = str(j.get("id_icims") or j.get("id", ""))
                if not jid or jid in seen:
                    continue
                seen.add(jid)
                jobs.append(Job(
                    company=cfg["name"],
                    external_id=jid,
                    title=j.get("title", ""),
                    url="https://www.amazon.jobs{}".format(j.get("job_path", "")),
                    locations=[j.get("normalized_location", "")],
                    posted=as_date(j.get("posted_date")),
                ))
            offset += PAGE
            if not batch or offset >= data.get("hits", 0):
                break
            time.sleep(0.5)
    return jobs
