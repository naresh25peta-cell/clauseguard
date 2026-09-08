# ClauseGuard — Project Brief

## What is ClauseGuard?
A learning project exploring how an LLM-based assistant could help a contracts/trading
team query and check agreements using natural language, instead of manually
cross-referencing PDFs against a rules database.

## Two Features

### 1. Nomination Rule Compliance Checking
- Extract fields from Cargo Nomination (CN) PDFs
- Compare extracted fields against a NominationRules table
- Join on AgreementGuid + TradeGroupId (1-to-many — row selection handled by the scorer)
- Field-specific prompts + LLM scoring (1-5 scale) per field

### 2. MSA Risk Matrix
- Scan Master Sales Agreement (MSA) documents, flag risks clause by clause
- 3 use cases: periodic runs, CMO checks, draft MSA validation
- Output: Red / Amber / Green risk ratings per clause

---

## Tech Stack

| Component           | Choice                 |
|----------------------|------------------------|
| LLM                  | OpenAI-compatible API  |
| Database             | SQLite                 |
| Document storage     | Local PDF files        |
| Interface            | FastAPI + CLI          |
| Dependency management| Poetry                 |

---

## Goal
Build a working pipeline that can be run and understood end-to-end: PDF extraction,
rule comparison, LLM scoring, and clause-level risk scanning, with clear reasoning
at each step rather than a black-box output.

---

## Build Order
1. Folder structure + environment setup (Poetry, .env)
2. PDF extraction pipeline (CN documents to structured fields)
3. SQLite schema + NominationRules comparison logic
4. LLM scoring function (1-5 scale)
5. MSA risk matrix scanner (clause-by-clause, Red/Amber/Green output)
6. FastAPI or CLI runner to tie it all together
