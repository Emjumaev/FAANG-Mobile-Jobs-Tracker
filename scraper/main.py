"""Orchestrator: fetch every company, keep mobile-engineering roles, diff, render README.

Usage:
    python -m scraper.main             # scrape all companies
    python -m scraper.main Google Meta # scrape a subset (for debugging)

Exit code is non-zero only on total failure; individual company failures are
reported (and written to data/health.json) but don't fail the run.
"""
import json
import os
import sys
import time
import traceback

from . import store
from .companies import COMPANIES
from .mobile import classify
from .render_readme import render

HEALTH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "health.json")


def run(only=None):
    all_jobs, succeeded, failed = [], set(), {}

    for cfg in COMPANIES:
        name = cfg["name"]
        if only and name not in only:
            continue
        try:
            fetched = cfg["fetch"](cfg)
            mobile = []
            for j in fetched:
                if not j.url:
                    continue
                labels = classify(j.title)
                if labels:
                    j.category, j.level = labels
                    mobile.append(j)
            print("[ok]   {:<20} {:>5} postings, {:>3} mobile".format(
                name, len(fetched), len(mobile)))
            all_jobs.extend(mobile)
            succeeded.add(name)
        except Exception as err:  # noqa: BLE001 - isolate per-company failures
            failed[name] = str(err)
            print("[FAIL] {:<20} {}".format(name, err))
            traceback.print_exc()
        time.sleep(1)

    if not succeeded:
        print("every scraper failed — aborting without touching data")
        return 1

    state = store.load()
    added, closed, reopened = store.merge(state, all_jobs, succeeded)
    store.save(state)
    render(state)

    os.makedirs(os.path.dirname(HEALTH_PATH), exist_ok=True)
    with open(HEALTH_PATH, "w") as fh:
        json.dump({"succeeded": sorted(succeeded), "failed": failed},
                  fh, indent=2, sort_keys=True)
        fh.write("\n")

    print("\nadded={} closed={} reopened={} | scrapers ok={} failed={}".format(
        len(added), len(closed), len(reopened), len(succeeded), len(failed)))
    for j in added:
        print("  + {} — {}".format(j["company"], j["title"]))

    # surface the counts to the GitHub Actions step that writes the commit message
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as fh:
            fh.write("added={}\nclosed={}\nfailed={}\n".format(
                len(added), len(closed), len(failed)))
    return 0


if __name__ == "__main__":
    sys.exit(run(only=set(sys.argv[1:]) or None))
