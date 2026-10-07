"""Holt die Live-Daten fürs Profil von der GitHub-API nach src/data/github.json.

Aufruf (Token als Umgebungsvariable, nie im Repo):
    PROFILE_TOKEN=... python3 scripts/fetch.py     # eigenes Token (inkl. privater Beiträge)
    GITHUB_TOKEN=...  python3 scripts/fetch.py     # Standard in der Action

Geholt wird in einer GraphQL-Abfrage:
  - Contribution-Kalender der letzten 52 Wochen (Summe je Woche)
  - Commits der laufenden Woche (ab Montag 00:00 UTC)
  - Anzahl öffentlicher eigener Repositories

Fehlerverhalten: Bei JEDEM Problem (kein Token, Netzwerk, API-Fehler,
unplausible Antwort) bleibt die vorhandene Datei unverändert. Das Skript
gibt eine Warnung aus und endet mit Exit-Code 0, damit die Action mit dem
letzten Stand weiterbaut. Geschrieben wird atomar (erst temporär, dann
umbenennen), damit nie eine halbe Datei entsteht.

Nur Python-Standardbibliothek.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "github.json"
TOKENS = ROOT / "src" / "design" / "tokens.json"
API = "https://api.github.com/graphql"
WEEKS = 52

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!, $weekFrom: DateTime!) {
  user(login: $login) {
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    year: contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { firstDay contributionDays { contributionCount } }
      }
    }
    week: contributionsCollection(from: $weekFrom, to: $to) {
      totalCommitContributions
    }
  }
}
"""


def warn(message):
    # ::warning:: erscheint in GitHub Actions als gelbe Anmerkung im Lauf
    print(f"::warning::fetch: {message} – vorhandene Daten bleiben unverändert.")


def query(token, login, now):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    variables = {
        "login": login,
        "from": (now - timedelta(weeks=WEEKS)).isoformat(),
        "to": now.isoformat(),
        "weekFrom": monday.isoformat(),
    }
    request = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{login}-profile-readme"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def parse(payload, login, now):
    """API-Antwort -> unser Datenformat. Wirft ValueError bei Unplausiblem."""
    if payload.get("errors"):
        raise ValueError("API meldet Fehler: " + "; ".join(e.get("message", "?") for e in payload["errors"]))
    user = (payload.get("data") or {}).get("user")
    if not user:
        raise ValueError(f"Benutzer '{login}' nicht gefunden")
    weeks = [
        {"start": w["firstDay"], "count": sum(d["contributionCount"] for d in w["contributionDays"])}
        for w in user["year"]["contributionCalendar"]["weeks"]
    ][-WEEKS:]
    if len(weeks) < WEEKS - 1:
        raise ValueError(f"nur {len(weeks)} Wochen im Kalender")
    return {
        "login": login,
        "fetched_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "weeks": weeks,
        "total": sum(w["count"] for w in weeks),
        "commits_this_week": user["week"]["totalCommitContributions"],
        "public_repos": user["repositories"]["totalCount"],
    }


def main():
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
    login = (os.environ.get("PROFILE_LOGIN")
             or json.loads(TOKENS.read_text(encoding="utf-8"))["profile"]["login"])
    if not token:
        warn("kein Token gesetzt (PROFILE_TOKEN oder GITHUB_TOKEN)")
        return 0
    now = datetime.now(timezone.utc)
    try:
        data = parse(query(token, login, now), login, now)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as exc:
        warn(f"{type(exc).__name__}: {exc}")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(OUT)
    print(f"fetch: {len(data['weeks'])} Wochen, {data['total']} Contributions, "
          f"{data['commits_this_week']} Commits diese Woche, {data['public_repos']} öffentliche Repos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
