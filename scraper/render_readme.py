"""Render README.md from data/jobs.json. The README is generated — never hand-edit."""
import os
from collections import Counter
from datetime import datetime, timedelta, timezone

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
NEW_BADGE_DAYS = 7
LEVEL_ORDER = ["Intern", "Entry", "Mid", "Senior", "Staff+", "Manager"]

HEADER = """\
# 📱 Mobile Engineering Jobs Tracker — Big Tech

Auto-updated list of **open mobile-engineering jobs** — iOS, Android,
Flutter / React Native / Kotlin Multiplatform and general mobile roles, from
internships to engineering managers — at {n_companies} FAANG and other big
tech companies, scraped directly from each company's careers API every
6 hours by GitHub Actions.

🌐 **Check out the web version of the project: [emjumaev.github.io/FAANG-Mobile-Jobs-Tracker](https://emjumaev.github.io/FAANG-Mobile-Jobs-Tracker/)**

> 🕐 Last updated: **{updated}** · 📌 **{n_open}** open mobile jobs
> · 🆕 = added in the last {new_days} days

{platforms}

⭐ Star this repo to keep an eye on new openings — or watch *Releases/Activity* for commits titled “new mobile job(s)”.

"""

FOOTER = """
---

## How this works

A [Python scraper](scraper/) queries each company's official careers API
(Greenhouse, Ashby, Workday, Eightfold, Phenom or their in-house endpoints)
for *iOS / Android / mobile / Flutter / React Native*, keeps only titles
that are mobile **engineering** roles — not product, design, sales or
telecom jobs that merely mention mobile ([scraper/mobile.py](scraper/mobile.py)) —
labels each with a platform and seniority, and diffs against
[`data/jobs.json`](data/jobs.json). A GitHub Actions
[workflow](.github/workflows/update.yml) runs it on a cron schedule and commits
only when something changed. Positions that disappear from a careers page are
closed automatically.

Found a problem or want another company added? Open an issue or PR.
"""


def _slug(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def _md_escape(text):
    return text.replace("|", "\\|").strip()


def _fmt_locations(locations, limit=3):
    locs = [l for l in locations if l]
    if not locs:
        return "—"
    shown = "; ".join(_md_escape(l) for l in locs[:limit])
    extra = len(locs) - limit
    if extra > 0:
        shown += " *(+{} more)*".format(extra)
    return shown


def _platform_line(jobs):
    counts = Counter(j.get("category") or "Mobile" for j in jobs)
    order = ["iOS", "Android", "iOS & Android", "Cross-platform", "Mobile"]
    parts = ["**{}** {}".format(counts[p], p) for p in order if counts[p]]
    levels = Counter(j.get("level") or "Mid" for j in jobs)
    lparts = ["{} {}".format(levels[l], l) for l in LEVEL_ORDER if levels[l]]
    return "> 📊 By platform: {}\n> · By level: {}".format(
        " · ".join(parts) or "—", " · ".join(lparts) or "—")


def render(state):
    from .companies import COMPANIES, UNSUPPORTED
    tracked = [c["name"] for c in COMPANIES]
    jobs = [j for j in state["jobs"].values() if j.get("active", True)]
    updated = state.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEW_BADGE_DAYS)).strftime("%Y-%m-%d")

    by_company = {name: [] for name in tracked}
    for j in jobs:
        by_company.setdefault(j["company"], []).append(j)

    companies = sorted(by_company)
    out = [HEADER.format(
        n_companies=len(companies),
        updated=updated.replace("T", " ").replace("Z", " UTC"),
        n_open=len(jobs),
        new_days=NEW_BADGE_DAYS,
        platforms=_platform_line(jobs),
    )]

    # summary table with anchors
    out.append("| Company | Open mobile jobs |\n|---|---|\n")
    for c in companies:
        n = len(by_company[c])
        label = "[{}](#{})".format(c, _slug(c)) if n else c
        out.append("| {} | {} |\n".format(label, n or "—"))
    for name, why in sorted(UNSUPPORTED.items()):
        out.append("| {} | *{}* |\n".format(name, why))
    out.append("\n---\n\n")

    for c in companies:
        if not by_company[c]:
            continue
        rows = sorted(by_company[c],
                      key=lambda j: (j.get("posted") or j.get("first_seen", ""),
                                     j["title"]),
                      reverse=True)
        out.append("## {}\n\n".format(c))
        out.append("| Role | Platform | Level | Location | Posted | First seen |\n"
                   "|---|---|---|---|---|---|\n")
        for j in rows:
            badge = " 🆕" if j.get("first_seen", "") >= cutoff else ""
            out.append("| [{}]({}){} | {} | {} | {} | {} | {} |\n".format(
                _md_escape(j["title"]), j["url"], badge,
                j.get("category") or "—",
                j.get("level") or "—",
                _fmt_locations(j.get("locations", [])),
                j.get("posted") or "—",
                j.get("first_seen", "—"),
            ))
        out.append("\n")

    out.append(FOOTER)
    with open(README_PATH, "w") as fh:
        fh.write("".join(out))
