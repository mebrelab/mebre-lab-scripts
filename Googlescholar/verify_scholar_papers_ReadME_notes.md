🔎 Google Scholar Authorship Verification Tool

A robust, transparent, and research-grade Python tool to verify whether publications listed on a Google Scholar profile are genuinely authored by the claimed scholar.

This tool is designed for:

Researchers validating their own publication records

Institutions auditing scholar profiles

Research integrity and bibliometric analysis

Teaching authorship verification methods

✨ Key Features

✅ Interactive prompts (no complex CLI arguments needed)

✅ Supports optional strong identity anchors:

ORCID iD

Scopus Author ID

ResearcherID / Publons ID

✅ Cross-checks publications using:

Crossref

Semantic Scholar

✅ Transparent confidence scoring (0–100, capped)

✅ Clear classification of each publication

✅ CSV report automatically named after the author

✅ Self-check mode for ethical transparency

✅ Human-readable terminal output + machine-readable CSV

🧠 Verification Logic (High-level)

For each publication listed on Google Scholar, the tool:

Retrieves external bibliographic records (Crossref, Semantic Scholar)

Compares:

Title similarity

Author name match (full name, last name, initials)

DOI presence

Boosts confidence when trusted identifiers are provided (ORCID, etc.)

Assigns:

A confidence score (0–100)

A classification

A verification strength label

No single signal is treated as absolute truth — the system is conservative and explainable by design.

🏷️ Classification Labels
Label	Meaning
AUTHENTIC	Strong evidence the work belongs to the scholar
LIKELY AUTHENTIC	Good metadata match, minor uncertainty
SCHOLAR-CLAIMED OUTPUT	Listed on Scholar but not externally indexed
LIKELY MISATTRIBUTED	Weak match; possible misattribution
🧪 Verification Strength (CSV column)
Value	Interpretation
Strong (ORCID + DOI)	Best-case verification
Moderate (Name + DOI)	Solid bibliographic match
Basic (Scholar-only)	Scholar-listed, no external index

This helps reviewers quickly understand why a decision was made.

🚀 Installation
1️⃣ Clone the repository
git clone https://github.com/yourusername/google-scholar-authorship-verifier.git
cd google-scholar-authorship-verifier

2️⃣ Install dependencies
pip install scholarly rapidfuzz requests


💡 Python 3.8+ recommended

▶️ Usage (Interactive – Recommended)

Simply run:

python verify_scholar_papers.py


You’ll be prompted step-by-step:

▶ Enter FULL author name (required)
▶ Enter Google Scholar ID (without &hl=)

(Optional identifiers — press Enter to skip)
▶ ORCID iD
▶ Scopus Author ID
▶ ResearcherID / Publons ID


No flags. No confusion.

🧾 Self-Check Mode (Recommended for transparency)

If you are verifying your own publications, use:

python verify_scholar_papers.py --self-check


The output will explicitly state:

🧾 Mode: SELF-CHECK (verification run by profile owner)

This is important for ethical clarity and methodological transparency.

📄 Output
1️⃣ Terminal Output

Per-publication classification

Confidence score

Final summary line

Example:

✅ Summary: 12/12 publications verified as AUTHENTIC (100%)

2️⃣ CSV Report

Automatically saved as:

verification_report_<author_name>.csv


Example columns:

claimed_title

matched_title

matched_source

doi

confidence_score

classification

verification_strength

reason

📊 Example Use Case
Author: Mebrahtom Gebresemati Weldehans
Scholar ID: u7e8zxgAAAAJ
ORCID: 0000-0002-8874-6784


Result:

AUTHENTIC (100.0)
Verification strength: Strong (ORCID + DOI)

⚠️ Important Notes & Limitations

Google Scholar profiles are self-curated

Not all legitimate outputs have DOIs (especially reports, theses, local journals)

The tool avoids “black-box certainty” on purpose

Results should be interpreted as decision support, not absolute proof

This design choice makes the tool suitable for academic and institutional contexts.

📚 Citation / Acknowledgment

If you use or adapt this tool in research, audits, or teaching, please cite it as:

Google Scholar Authorship Verification Tool, GitHub repository, YYYY.