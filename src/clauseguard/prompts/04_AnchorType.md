# AnchorType

- **Output type / allowed values:** One of: WindowStart, InitialWindow, Commented, SalesWindow, SpecificDate, Unknown
- **Status:** Already LLM-friendly — no rewording required.
- **Open question for SME:** 'SalesWindow' appears in the allowed list but is never defined in the prompt — confirm its meaning and when it should be returned vs WindowStart / InitialWindow.

## Extraction instruction

> Standard intro applies first — see [00_standard_intro.md](00_standard_intro.md).

Single value identifying the reference point for when the updated term must be provided. Locate the clause stating the deadline (e.g. 'no later than 14 days prior to the start of the initial delivery window'). Use SpecificDate where a precise date is stated with no calculation method. Use Commented where the logic is more complex than a single number of days to a single anchor point.
