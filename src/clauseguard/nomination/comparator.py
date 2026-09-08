"""
comparator.py — compares extracted CN fields against NominationRules rows,
                scores each field via the LLM (1–5), and writes results to CNExtractions.

Flow:
  1. AgreementGuid + TradeGroupId are supplied by the caller (from deal context —
     they identify which contract / trade group to compare against).
     These are NOT extracted from the PDF; they are identity columns known from
     the deal ticket or email.
  2. Look up NominationRules rows matching AgreementGuid + TradeGroupId.
     One TradeGroupId can have 0–N rules (median 1, max ~10 per PROFILE.md).
  3. For each rule row, score each of the 7 extracted fields against the
     corresponding RulesDB column (1–5 scale).
  4. Write every scored result to CNExtractions for audit / history.
  5. Return a summary list for display.
"""
from clauseguard.database.schema import get_connection
from clauseguard.nomination.scorer import score_field

# The 7 fields extracted from the PDF that have matching RulesDB columns.
EXTRACTION_FIELDS = [
    "NominationRuleDescription",
    "AgreementSection",
    "OptionOwner",
    "AnchorType",
    "Complexity",
    "AnchorDirection",
    "NominationRuleTitle",
]


def compare_and_score(
    pdf_filename: str,
    extracted: dict,
    agreement_guid: str,
    trade_group_id: str,
) -> list[dict]:
    """
    Compare extracted fields against NominationRules and store scored results.

    Args:
        pdf_filename   : original PDF filename (stored for audit trail)
        extracted      : dict from pdf_extractor.extract_fields()
        agreement_guid : from deal context — used to JOIN RulesDB
        trade_group_id : from deal context — used to JOIN RulesDB

    Returns:
        List of result dicts, one per field scored.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Fetch matching NominationRules rows (0-to-N per TradeGroupId)
    cur.execute("""
        SELECT NominationRuleId,
               NominationRuleDescription, AgreementSection, OptionOwner,
               AnchorType, Complexity, AnchorDirection, NominationRuleTitle
        FROM   NominationRules
        WHERE  AgreementGuid = ? AND TradeGroupId = ?
    """, (agreement_guid, trade_group_id))
    rules = cur.fetchall()

    if not rules:
        print(f"  No NominationRules found for AgreementGuid={agreement_guid}, TradeGroupId={trade_group_id}")
        conn.close()
        return []

    results = []
    for rule in rules:
        rule_id = rule["NominationRuleId"]

        for field_name in EXTRACTION_FIELDS:
            field_data      = extracted.get(field_name) or {}
            # support both the new dict format {"value":…,"quote":…} and plain strings
            if isinstance(field_data, dict):
                extracted_value = field_data.get("value")
                extracted_quote = field_data.get("quote", "")
            else:
                extracted_value = field_data
                extracted_quote = ""
            expected_value  = rule[field_name]

            score, reasoning = score_field(
                field_name=field_name,
                extracted_value=extracted_value,
                expected_value=expected_value,
            )

            cur.execute("""
                INSERT INTO CNExtractions
                    (FileName, AgreementGuid, TradeGroupId, FieldName,
                     ExtractedValue, ExpectedValue, LLMScore, ScoreReasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pdf_filename, agreement_guid, trade_group_id, field_name,
                str(extracted_value) if extracted_value is not None else None,
                str(expected_value)  if expected_value  is not None else None,
                score, reasoning,
            ))

            results.append({
                "rule_id":   rule_id,
                "field":     field_name,
                "extracted": extracted_value,
                "quote":     extracted_quote,
                "expected":  expected_value,
                "score":     score,
                "reasoning": reasoning,
            })

    conn.commit()
    conn.close()
    return results
