# Raw outputs manifest

This folder contains unedited JSON emitted by actual NyayaSaathi pipeline runs.

## Problem 1: full supplied PDF pack

- `problem1_document_inventory.json` - PyMuPDF inspection of all six supplied PDFs.
- `problem1_parsing_report.json` - parsing and chunking run report.
- `retrieval_20261108T135300Z.json` - multilingual retrieval evaluation over the fixed evaluation set.

## Problem 2: self-authored consumer test cases

- `problem2_chat_smoke_defective_phone.json` - complete end-to-end Gemini result for a defective-phone refund scenario.
- `problem2_chat_outputs_20261108T135820Z.json` - two complete end-to-end Gemini chat cases: defective-phone refund and Hinglish refund denial. Each record includes the original query, unedited fact extraction, resulting case state, structured legal answer, citations, and retrieved chunks.

Timestamps are UTC. The files preserve model outputs rather than editorial summaries.
