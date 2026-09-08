# Complexity

- **Output type / allowed values:** One of: DateExpression, SimpleAnchor
- **Status:** Already LLM-friendly — no rewording required.
- **Open question for SME:** Confirm exact spelling/casing of the two values as stored in RulesDB.

## Extraction instruction

> Standard intro applies first — see [00_standard_intro.md](00_standard_intro.md).

Return DateExpression where the timing logic is more complex than a single number of days to a single anchor point; otherwise return SimpleAnchor.
