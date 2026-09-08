"""
risk_scanner.py — scans an MSA (Master Sales Agreement) PDF clause by clause,
                  rates each clause Red / Amber / Green, and stores results.

Three use cases:
  periodic       : scheduled background scan of known MSA documents
  cmo_check      : CMO (Chief Marketing Officer) spot-check before a deal
  draft_validation: validate a draft MSA before it is signed

How clause splitting works:
  We look for patterns like "Clause 1", "1.", "Section 2.3" etc.
  This is a best-effort split — MSA formats vary by counterparty.

Risk rating definitions:
  Red   : clause poses significant legal or commercial risk; needs review
  Amber : clause has moderate risk or ambiguity; flag for attention
  Green : clause is standard / acceptable
"""
import re
import json
import pdfplumber
from openai import OpenAI
from clauseguard.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from clauseguard.database.schema import get_connection

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# Regex that splits text at common clause heading patterns
CLAUSE_SPLIT_PATTERN = re.compile(
    r'(?=(?:clause|section|article)\s+\d[\d.]*\b)',
    flags=re.IGNORECASE,
)


def _extract_text(pdf_path: str) -> str:
    """Read all pages of an MSA PDF and return combined text."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _split_clauses(text: str) -> list[dict]:
    """
    Split MSA text into clause chunks.
    Returns list of {"ref": "Clause 1", "text": "..."} dicts.

    Falls back to fixed-size chunks if no clause markers are found,
    so the scanner still works on non-standard documents.
    """
    parts = CLAUSE_SPLIT_PATTERN.split(text)
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) <= 1:
        # No clause markers found — chunk by paragraph instead
        parts = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]

    clauses = []
    for part in parts:
        # Extract a short ref from the first line (e.g. "Clause 12.3 Termination")
        first_line = part.split("\n")[0][:80]
        clauses.append({"ref": first_line, "text": part})

    return clauses


def _rate_clause(clause_ref: str, clause_text: str, use_case: str) -> tuple[str, str]:
    """
    Ask the LLM to rate a single clause Red / Amber / Green.

    Returns:
        (rating, reasoning)
    """
    use_case_context = {
        "periodic":          "This is a periodic compliance review of a live MSA.",
        "cmo_check":         "The CMO needs a quick risk summary before approving a deal.",
        "draft_validation":  "This is a draft MSA — flag anything that needs negotiation before signing.",
    }.get(use_case, "This is a general MSA risk review.")

    prompt = f"""
You are a legal risk analyst reviewing an LNG trading Master Sales Agreement (MSA).

Context: {use_case_context}

Clause reference: {clause_ref}
Clause text:
---
{clause_text[:2000]}
---

Rate this clause:
  Red   = significant legal or commercial risk; requires immediate review
  Amber = moderate risk or ambiguity; flag for attention
  Green = standard / acceptable clause

Respond with ONLY valid JSON:
{{"rating": "Red" | "Amber" | "Green", "reasoning": "<one or two sentence explanation>"}}
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result["rating"], result["reasoning"]


def scan_msa(pdf_path: str, use_case: str = "periodic") -> list[dict]:
    """
    Full MSA scan: extract → split → rate each clause → store → return results.

    Args:
        pdf_path : path to MSA PDF file
        use_case : "periodic", "cmo_check", or "draft_validation"

    Returns:
        List of dicts with keys: clause_ref, rating, reasoning
    """
    import os
    pdf_filename = os.path.basename(pdf_path)

    print(f"  Extracting text from {pdf_filename}...")
    text = _extract_text(pdf_path)

    clauses = _split_clauses(text)
    print(f"  Found {len(clauses)} clauses to rate.")

    conn = get_connection()
    cur = conn.cursor()
    results = []

    for clause in clauses:
        ref  = clause["ref"]
        body = clause["text"]

        rating, reasoning = _rate_clause(ref, body, use_case)

        cur.execute("""
            INSERT INTO MSARiskResults (FileName, ClauseRef, ClauseText, RiskRating, Reasoning, UseCase)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pdf_filename, ref, body[:500], rating, reasoning, use_case))

        results.append({"clause_ref": ref, "rating": rating, "reasoning": reasoning})

    conn.commit()
    conn.close()
    return results
