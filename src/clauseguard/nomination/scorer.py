"""
scorer.py — asks the LLM to score how well an extracted CN field matches
            the expected value stored in the rules database.

Score scale:
  1 = completely wrong / missing
  2 = significant mismatch
  3 = partial match
  4 = minor difference
  5 = exact or fully acceptable match

Why LLM scoring instead of string equality?
  Values like "seller" and "Solace Energy Trading Ltd" refer to the same party.
  A string compare would fail; an LLM understands they match.
"""
import json
from openai import OpenAI
from clauseguard.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


def score_field(
    field_name: str,
    extracted_value: str | None,
    expected_value: str | None,
) -> tuple[int, str]:
    """
    Score one field comparison using the LLM.
    Returns (score, reasoning) where score is 1–5.
    """
    prompt = f"""
You are validating a nomination-rule field extracted from an LNG contract PDF
against the expected value stored in the rules database.

Field name      : {field_name}
Extracted value : {extracted_value if extracted_value is not None else "NOT FOUND"}
Expected value  : {expected_value  if expected_value  is not None else "NOT IN RULES DATABASE"}

Score the match on this scale:
  1 = completely wrong or field missing
  2 = significant mismatch
  3 = partial match (e.g. correct concept, wrong wording)
  4 = minor difference (e.g. capitalisation, abbreviation)
  5 = exact or fully acceptable match

Respond with ONLY valid JSON:
{{"score": <integer 1-5>, "reasoning": "<one sentence explanation>"}}
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return int(result["score"]), result["reasoning"]
