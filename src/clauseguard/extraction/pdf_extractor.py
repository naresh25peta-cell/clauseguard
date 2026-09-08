"""
pdf_extractor.py — extracts nomination-rule fields from a CN or MSA PDF.

How it works:
  1. pdfplumber reads the raw text from all PDF pages.
  2. For each target field, we build a prompt:
       [standard intro] + [field name + output type + instruction] + [source text]
  3. The LLM is called ONCE PER FIELD — not once for all fields together.
     Why: field-by-field calls are more accurate because each prompt is focused
     on a single extraction task with a clear output type constraint.
  4. Results are collected into a dict and returned.

Fields extracted (matching RulesDB NominationRules columns):
  NominationRuleDescription, AgreementSection, OptionOwner, AnchorType,
  Complexity, AnchorDirection, NominationRuleTitle
"""
import time
import pdfplumber
from openai import OpenAI, RateLimitError
from clauseguard.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from clauseguard.extraction.prompt_loader import load_standard_intro, load_fields, FieldSpec

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, max_retries=0)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Read all pages of a PDF and return the combined text."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def build_field_prompt(field: FieldSpec, standard_intro: str, source_text: str) -> str:
    """
    Compose the per-field prompt sent to the LLM.
    Shape: [intro] [field name + output type + instruction] [source text] [final ask].
    """
    parts = [
        standard_intro.strip(),
        "",
        f"Field to extract: {field.name}",
        f"Output type / allowed values: {field.output_type}",
        "",
        "Extraction instruction:",
        field.instruction.strip(),
        "",
        "Source text:",
        source_text.strip(),
        "",
        "Return your answer in exactly two lines:",
        "VALUE: <the extracted value, matching the output type above>",
        "QUOTE: <copy the exact sentence or short phrase from the source text that supports this value>",
        "",
        "No other text. No explanation. Just the two lines.",
    ]
    return "\n".join(parts)


def _call_llm(prompt: str) -> str:
    """Call the LLM with a single prompt, retrying automatically on rate limits."""
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2048,
            )
            return (response.choices[0].message.content or "").strip()
        except RateLimitError as e:
            wait = 35 * (attempt + 1)
            print(f"  Rate limited — waiting {wait}s before retry (attempt {attempt+1}/5)...")
            time.sleep(wait)
    raise RuntimeError("LLM call failed after 5 retries due to rate limiting.")


def _parse_response(raw: str) -> dict[str, str]:
    """
    Parse the VALUE:/QUOTE: two-line response from the LLM.
    Falls back gracefully if the LLM doesn't follow the format exactly.
    """
    value = ""
    quote = ""
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("VALUE:"):
            value = stripped[6:].strip()
        elif stripped.upper().startswith("QUOTE:"):
            quote = stripped[6:].strip()
    # Fallback: if the LLM returned plain text (no labels), treat the whole
    # response as the value and leave quote empty.
    if not value:
        value = raw.strip()
    return {"value": value, "quote": quote}


def extract_fields(pdf_path: str) -> dict[str, dict[str, str]]:
    """
    Extract all nomination-rule fields from a CN PDF, one LLM call per field.

    Returns a dict keyed by RulesDB column name.  Each value is:
        {"value": <extracted value>, "quote": <supporting clause text>}
    """
    source_text = extract_text_from_pdf(pdf_path)
    standard_intro = load_standard_intro()
    fields = load_fields()

    result: dict[str, dict[str, str]] = {}
    for field in fields:
        prompt = build_field_prompt(field, standard_intro, source_text)
        raw = _call_llm(prompt)
        result[field.name] = _parse_response(raw)

    return result


if __name__ == "__main__":
    import json, sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/pdfs/cn/sample.pdf"
    print(json.dumps(extract_fields(path), indent=2))
