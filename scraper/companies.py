"""Company registry. Every entry: display name + adapter fetch fn + its config.

FAANG plus the other big tech, fintech and consumer-app employers that run
sizeable iOS/Android teams. Endpoints were each verified by hand (2026-10).
If one breaks, the workflow opens a `scraper-health` issue automatically —
see .github/workflows/update.yml.
"""
from .adapters import (amazon, apple, ashby, bloomberg, eightfold,
                       github_careers, google, greenhouse, meta, microsoft,
                       oracle_hcm, phenom, spotify, workday)

# Companies we can't cover, and why — rendered into the README summary table.
UNSUPPORTED = {
    "Tesla": ("careers site and its JSON API sit behind Akamai bot protection "
              "that returns 403 to every non-browser client; needs a headless browser"),
    "ByteDance / TikTok": ("joinbytedance.com's job-search API rejects requests that "
                           "don't carry its in-browser client signature; needs a headless browser"),
    "Qualcomm": ("Eightfold-hosted careers.qualcomm.com returns 403 to every "
                 "non-browser client; needs a headless browser"),
    "Uber": ("careers moved to jobs.uber.com, which sits behind bot protection "
             "that returns 403 to every non-browser client; needs a headless browser"),
    "LinkedIn": ("careers site only links to linkedin.com/jobs, which is "
                 "authwalled and prohibits scraping"),
}

COMPANIES = [
    # --- Greenhouse boards ---------------------------------------------------
    {"name": "Airbnb", "fetch": greenhouse.fetch, "token": "airbnb"},
    {"name": "Anthropic", "fetch": greenhouse.fetch, "token": "anthropic"},
    {"name": "Cloudflare", "fetch": greenhouse.fetch, "token": "cloudflare"},
    {"name": "Databricks", "fetch": greenhouse.fetch, "token": "databricks"},
    {"name": "Pinterest", "fetch": greenhouse.fetch, "token": "pinterest"},
    {"name": "Stripe", "fetch": greenhouse.fetch, "token": "stripe"},
    {"name": "Dropbox", "fetch": greenhouse.fetch, "token": "dropbox"},
    {"name": "Reddit", "fetch": greenhouse.fetch, "token": "reddit"},
    {"name": "Scale AI", "fetch": greenhouse.fetch, "token": "scaleai"},
    {"name": "Waymo", "fetch": greenhouse.fetch, "token": "waymo"},
    {"name": "Figma", "fetch": greenhouse.fetch, "token": "figma"},
    {"name": "DoorDash", "fetch": greenhouse.fetch, "token": "doordashusa"},
    {"name": "Lyft", "fetch": greenhouse.fetch, "token": "lyft"},
    {"name": "Coinbase", "fetch": greenhouse.fetch, "token": "coinbase"},
    {"name": "MongoDB", "fetch": greenhouse.fetch, "token": "mongodb"},
    {"name": "Duolingo", "fetch": greenhouse.fetch, "token": "duolingo"},
    {"name": "Robinhood", "fetch": greenhouse.fetch, "token": "robinhood"},
    {"name": "Instacart", "fetch": greenhouse.fetch, "token": "instacart"},
    {"name": "Twitch", "fetch": greenhouse.fetch, "token": "twitch"},
    {"name": "Tripadvisor", "fetch": greenhouse.fetch, "token": "tripadvisor"},
    {"name": "Mozilla", "fetch": greenhouse.fetch, "token": "mozilla"},
    {"name": "Deliveroo", "fetch": greenhouse.fetch, "token": "deliveroo"},
    {"name": "Wolt", "fetch": greenhouse.fetch, "token": "wolt"},
    {"name": "Epic Games", "fetch": greenhouse.fetch, "token": "epicgames"},
    {"name": "Riot Games", "fetch": greenhouse.fetch, "token": "riotgames"},
    {"name": "Block", "fetch": greenhouse.fetch, "token": "block"},
    {"name": "Roblox", "fetch": greenhouse.fetch, "token": "roblox"},
    {"name": "Affirm", "fetch": greenhouse.fetch, "token": "affirm"},
    {"name": "Monzo", "fetch": greenhouse.fetch, "token": "monzo"},
    {"name": "N26", "fetch": greenhouse.fetch, "token": "n26"},
    {"name": "Proton", "fetch": greenhouse.fetch, "token": "proton"},
    {"name": "Coupang", "fetch": greenhouse.fetch, "token": "coupang"},
    {"name": "Adyen", "fetch": greenhouse.fetch, "token": "adyen"},
    {"name": "SumUp", "fetch": greenhouse.fetch, "token": "sumup"},

    # --- Ashby ---------------------------------------------------------------
    {"name": "OpenAI", "fetch": ashby.fetch, "org": "openai"},

    # --- Workday CXS ---------------------------------------------------------
    {"name": "NVIDIA", "fetch": workday.fetch,
     "host": "nvidia.wd5.myworkdayjobs.com", "site": "NVIDIAExternalCareerSite"},
    {"name": "Adobe", "fetch": workday.fetch,
     "host": "adobe.wd5.myworkdayjobs.com", "site": "external_experienced"},
    {"name": "Salesforce", "fetch": workday.fetch,
     "host": "salesforce.wd12.myworkdayjobs.com", "site": "External_Career_Site"},
    {"name": "Intel", "fetch": workday.fetch,
     "host": "intel.wd1.myworkdayjobs.com", "site": "External"},
    {"name": "PayPal", "fetch": workday.fetch,
     "host": "paypal.wd1.myworkdayjobs.com", "site": "jobs"},
    {"name": "Snap", "fetch": workday.fetch,
     "host": "snapchat.wd1.myworkdayjobs.com", "tenant": "snapchat", "site": "snap"},

    # --- Eightfold -----------------------------------------------------------
    {"name": "Netflix", "fetch": eightfold.fetch,
     "host": "explore.jobs.netflix.net", "domain": "netflix.com"},

    # --- Phenom (/widgets) ---------------------------------------------------
    {"name": "Cisco", "fetch": phenom.fetch, "host": "careers.cisco.com",
     "job_url": "https://careers.cisco.com/global/en/job/{id}"},
    {"name": "Snowflake", "fetch": phenom.fetch, "host": "careers.snowflake.com",
     "job_url": "https://careers.snowflake.com/us/en/job/{id}",
     "body_overrides": {"lang": "en_us", "country": "us",
                        "all_fields": ["category", "country", "state", "city", "type"]}},

    # --- Custom --------------------------------------------------------------
    {"name": "Google", "fetch": google.fetch},
    {"name": "Meta", "fetch": meta.fetch},
    {"name": "Microsoft", "fetch": microsoft.fetch},
    {"name": "Amazon", "fetch": amazon.fetch},
    {"name": "Apple", "fetch": apple.fetch},
    {"name": "GitHub", "fetch": github_careers.fetch},
    {"name": "Oracle", "fetch": oracle_hcm.fetch},
    {"name": "Spotify", "fetch": spotify.fetch},
    {"name": "Bloomberg", "fetch": bloomberg.fetch},
]
