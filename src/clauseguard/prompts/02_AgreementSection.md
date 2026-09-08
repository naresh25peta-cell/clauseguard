# AgreementSection

- **Output type / allowed values:** One of: Vessel, LoadLocation, Quantity, DischargeLocation, ArrivalWindow, or blank
- **Status:** Already LLM-friendly — no rewording required.
- **Open question for SME:** Source prompt lists 'Vessel' twice and 'arrivalwindow' — confirm the canonical list, casing, and whether 'ArrivalWindow' is distinct from a delivery/sales window.

## Extraction instruction

> Standard intro applies first — see [00_standard_intro.md](00_standard_intro.md).

The contractual term the party has the right to update — a single value from the allowed list. Where the nomination relates to something outside these (e.g. credit terms, contract duration, right to cancel or terminate deliveries), return blank.
