#!/usr/bin/env python3
"""
verify_scholar_papers.py
==================================================
Interactive authorship verification for Google
Scholar profiles using bibliographic cross-checking.

Modes:
- Interactive prompts (default)
- --self-check : declare profile-owner verification

Required (prompted):
- Full author name
- Google Scholar Author ID

Optional (prompted):
- ORCID iD
- Scopus Author ID
- ResearcherID / Publons ID
"""

import csv
import time
import random
import re
import argparse
from pathlib import Path
import requests
from scholarly import scholarly
from rapidfuzz import fuzz

# ==================================================
# Argument parsing (only for optional flags)
# ==================================================

def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Declare that the verification is run by the profile owner"
    )
    return parser.parse_known_args()[0]

# ==================================================
# Utilities
# ==================================================

def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

def last_name(full_name):
    return normalize(full_name).split()[-1]

def author_name_score(full_name, authors):
    full = normalize(full_name)
    last = last_name(full_name)
    initial = full[0]

    scores = []
    for a in authors:
        a = normalize(a)
        scores.extend([
            fuzz.partial_ratio(full, a),
            fuzz.partial_ratio(last, a),
            fuzz.partial_ratio(f"{initial} {last}", a)
        ])
    return max(scores) if scores else 0

def title_score(a, b):
    return fuzz.token_set_ratio(normalize(a), normalize(b))

def cap_score(score):
    return min(round(score, 2), 100.0)

# ==================================================
# External metadata APIs
# ==================================================

def crossref_lookup(title):
    try:
        r = requests.get(
            "https://api.crossref.org/works",
            params={"query.title": title, "rows": 3},
            timeout=30
        )
        if not r.ok:
            return []

        results = []
        for i in r.json()["message"]["items"]:
            results.append({
                "title": i.get("title", [""])[0],
                "authors": [
                    f"{a.get('given','')} {a.get('family','')}".strip()
                    for a in i.get("author", [])
                ],
                "doi": i.get("DOI"),
                "orcid": [
                    a.get("ORCID") for a in i.get("author", [])
                    if a.get("ORCID")
                ],
                "source": "Crossref"
            })
        return results
    except Exception:
        return []

def semantic_lookup(title):
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": title,
                "limit": 3,
                "fields": "title,authors,externalIds"
            },
            timeout=30
        )
        if not r.ok:
            return []

        results = []
        for d in r.json().get("data", []):
            results.append({
                "title": d.get("title", ""),
                "authors": [a["name"] for a in d.get("authors", [])],
                "doi": d.get("externalIds", {}).get("DOI"),
                "source": "SemanticScholar"
            })
        return results
    except Exception:
        return []

# ==================================================
# Identity bonus (bounded)
# ==================================================

def id_bonus(orcid, scopus_id, researcher_id, hit):
    bonus = 0
    if orcid and hit and orcid in (hit.get("orcid") or []):
        bonus += 15
    if scopus_id:
        bonus += 5
    if researcher_id:
        bonus += 5
    return min(bonus, 25)

# ==================================================
# Verification strength (NEW)
# ==================================================

def verification_strength(orcid, doi_present):
    if orcid and doi_present:
        return "Strong (ORCID + DOI)"
    if doi_present:
        return "Moderate (Name + DOI)"
    return "Basic (Scholar-only)"

# ==================================================
# Verification logic
# ==================================================

def verify_publication(pub, author_name, orcid, scopus_id, researcher_id):
    candidates = crossref_lookup(pub["title"]) + semantic_lookup(pub["title"])

    if not candidates:
        return build_result(
            pub, None, 85, "SCHOLAR-CLAIMED OUTPUT",
            "No external bibliographic record found",
            verification_strength(orcid, False)
        )

    best, best_score, best_author_score, best_doi = None, -1, 0, False

    for c in candidates:
        ts = title_score(pub["title"], c["title"])
        ascore = author_name_score(author_name, c["authors"])
        doi_present = bool(c.get("doi"))

        score = (
            0.65 * ts +
            0.25 * ascore +
            (5 if doi_present else 0) +
            id_bonus(orcid, scopus_id, researcher_id, c)
        )

        if score > best_score:
            best = c
            best_score = score
            best_author_score = ascore
            best_doi = doi_present

    if best_author_score >= 85:
        label = "AUTHENTIC"
    elif best_score >= 75:
        label = "LIKELY AUTHENTIC"
    elif best_score >= 60:
        label = "SCHOLAR-CLAIMED OUTPUT"
    else:
        label = "LIKELY MISATTRIBUTED"

    return build_result(
        pub,
        best,
        cap_score(best_score),
        label,
        "Automated bibliographic verification",
        verification_strength(orcid, best_doi)
    )

def build_result(pub, best, score, label, reason, strength):
    return {
        "claimed_title": pub["title"],
        "matched_title": best["title"] if best else "",
        "matched_source": best["source"] if best else "Google Scholar only",
        "doi": best.get("doi") if best else "",
        "confidence_score": score,
        "classification": label,
        "verification_strength": strength,
        "reason": reason
    }

# ==================================================
# Interactive input
# ==================================================

def prompt_inputs():
    print("\n🔎 Google Scholar Authorship Verification")
    print("--------------------------------------------------")

    name = input("▶ Enter FULL author name (required): ").strip()
    while not name:
        name = input("  ❗ Name cannot be empty: ").strip()

    scholar_id = input(
        "▶ Enter Google Scholar ID (required, without &hl=): "
    ).strip()
    while not scholar_id:
        scholar_id = input("  ❗ Scholar ID required: ").strip()

    print("\n(Optional identifiers — press Enter to skip)\n")
    orcid = input("▶ ORCID iD: ").strip() or None
    scopus_id = input("▶ Scopus Author ID: ").strip() or None
    researcher_id = input("▶ ResearcherID / Publons ID: ").strip() or None

    return name, scholar_id, orcid, scopus_id, researcher_id

# ==================================================
# Main
# ==================================================

def main():
    args = parse_args()
    name, scholar_id, orcid, scopus_id, researcher_id = prompt_inputs()

    print(f"\n📘 Verifying Scholar Profile: {name}")
    if args.self_check:
        print("🧾 Mode: SELF-CHECK (verification run by profile owner)")

    author = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=["publications"])

    pubs = [
        {"title": p["bib"].get("title")}
        for p in author["publications"]
        if p["bib"].get("title")
    ]

    print(f"\n📚 Found {len(pubs)} records\n")

    safe_name = normalize(name).replace(" ", "_")
    outfile = Path(f"verification_report_{safe_name}.csv")

    results = []
    authentic_count = 0

    for i, pub in enumerate(pubs, 1):
        print(f"🔎 [{i}/{len(pubs)}] {pub['title'][:70]}")
        res = verify_publication(pub, name, orcid, scopus_id, researcher_id)
        print(f"   → {res['classification']} ({res['confidence_score']})")
        if res["classification"] == "AUTHENTIC":
            authentic_count += 1
        results.append(res)
        time.sleep(2 + random.random())

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    percent = round((authentic_count / len(results)) * 100, 1)

    print(f"\n✅ Summary: {authentic_count}/{len(results)} publications verified as AUTHENTIC ({percent}%)")
    print(f"📄 Report saved: {outfile}")

if __name__ == "__main__":
    main()