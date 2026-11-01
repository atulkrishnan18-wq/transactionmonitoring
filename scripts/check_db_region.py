#!/usr/bin/env python3
"""
ScoreSentinel — Database Region Inspector (scripts/check_db_region.py)
Reads DATABASE_URL from the environment (or .env if present), inspects only
the hostname (never printing credentials), and reports whether the database
is hosted in AWS Mumbai (ap-south-1) or another region.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


AWS_REGION_RE = re.compile(
    r"\b("
    r"us-east-[12]|us-west-[12]|"
    r"af-south-1|"
    r"ap-east-1|ap-south-[12]|ap-northeast-[123]|ap-southeast-[12345]|"
    r"ca-central-1|ca-west-1|"
    r"eu-central-[12]|eu-west-[123]|eu-south-[12]|eu-north-1|"
    r"il-central-1|me-south-1|me-central-1|sa-east-1"
    r")\b",
    re.IGNORECASE,
)


def _load_database_url() -> str:
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if db_url:
        return db_url

    repo_root = Path(__file__).resolve().parent.parent
    env_file = repo_root / ".env"
    if env_file.exists():
        for raw_line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return val.strip().strip('"').strip("'")
    return ""


def inspect_region(db_url: str) -> str:
    if not db_url or db_url.upper() == "CHANGE_ME":
        return "Could not determine region from hostname"

    try:
        parsed = urlparse(db_url if "://" in db_url else f"postgresql://{db_url}")
        hostname = (parsed.hostname or "").lower()
    except Exception:
        hostname = ""

    if not hostname:
        return "Could not determine region from hostname"

    match = AWS_REGION_RE.search(hostname)
    if not match:
        return "Could not determine region from hostname"

    region = match.group(1).lower()
    if region == "ap-south-1":
        return "Mumbai (ap-south-1) - OK for India hosting"
    return f"NOT India-hosted: detected {region}"


def main() -> int:
    db_url = _load_database_url()
    result = inspect_region(db_url)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
