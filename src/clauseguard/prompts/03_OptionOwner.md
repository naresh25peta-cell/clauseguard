# OptionOwner

- **Output type / allowed values:** One of: seller, counterparty, mutual
- **Status:** Already LLM-friendly — no rewording required.
- **Open question for SME:** _(none)_

## Extraction instruction

> Standard intro applies first — see [00_standard_intro.md](00_standard_intro.md).

The party with the explicit right to change the field. Often stated as buyer or seller — convert to seller or counterparty based on who is named as buyer/seller in the agreement. Where a non-binding term is used (e.g. reasonable endeavours, a party shall not unreasonably withhold permission), return mutual.
