# FMP AI Scorer

This project scores California school district Facilities Master Plans (FMPs) for how well they address:

1. Outdoor spaces and campus greening
2. Climate risk and mitigation
3. Energy efficiency and resilience

The scorer extracts text from FMP PDFs, retrieves the most relevant evidence for each rubric area, sends that evidence to an OpenAI model, and writes structured scores, confidence labels, reasoning, and evidence summaries.

## Project Goal

The goal is to create a consistent, auditable AI-assisted scoring workflow for district-level Facilities Master Plans. The output should help compare districts on sustainability and resilience planning without requiring a reviewer to manually read hundreds of pages for every plan.

The system is designed to be conservative: it should not award high scores for vague references, isolated keywords, or generic facilities language unless the plan clearly meets the rubric criteria.

## Repository Contents

```text
.
├── requirements.txt
├── src/
│   ├── config.py
│   ├── pdf_utils.py
│   ├── chunking.py
│   ├── retrieval.py
│   ├── rubrics.py
│   ├── scoring.py
│   ├── pipeline.py
│   ├── pipeline_parent_context.py
│   └── run_score_fmps.py
└── data/
    └── output/
        ├── all_fmps_chunked_results.csv
        ├── chunk_prompt_test_3_results.csv
        └── parent_context_scores/
            └── all_fmps_parent_context_results.csv
```

Some local files may exist but are intentionally ignored by Git, including `.env`, PDFs, detailed JSON outputs, virtual environments, and experimental `FILE_*.py` scripts.

## Core Files

### `src/config.py`

Loads environment variables from `.env`, checks that `OPENAI_API_KEY` exists, and defines model/chunking settings:

- `MODEL_NAME`
- `TOP_K_CHUNKS`
- `CHUNK_PAGES`
- `CHUNK_OVERLAP`

The API key should stay only in `.env`. Do not hard-code it in Python files.

### `src/pdf_utils.py`

Handles PDF loading and text extraction using PyMuPDF.

Main functions:

- `load_pdf_from_path(pdf_path)`
- `extract_pdf_pages(pdf_bytes)`
- `clean_text(text)`

The output is a list of page dictionaries:

```python
{
    "page_num": 1,
    "text": "..."
}
```

### `src/chunking.py`

Contains deterministic page-based chunking.

Main functions:

- `chunk_pages(...)`
- `chunk_pages_with_parents(...)`

`chunk_pages()` is the original baseline chunking method. It creates overlapping page windows, usually 3 pages with 1 page of overlap.

`chunk_pages_with_parents()` supports the newer parent-context pipeline. It creates small child chunks for retrieval and attaches larger parent spans for scoring context.

### `src/retrieval.py`

Contains keyword-based retrieval logic.

The original retrieval path uses flat keyword lists:

- `OUTDOOR_KEYWORDS`
- `CLIMATE_KEYWORDS`
- `ENERGY_KEYWORDS`
- `retrieve_top_chunks(...)`

The parent-context path uses weighted keyword dictionaries, co-occurrence bonuses, and penalties for generic-only matches:

- `OUTDOOR_WEIGHTED_KEYWORDS`
- `CLIMATE_WEIGHTED_KEYWORDS`
- `ENERGY_WEIGHTED_KEYWORDS`
- `retrieve_top_parent_chunks(...)`

This file is intentionally deterministic so the retrieval process is reproducible and easier to debug.

### `src/rubrics.py`

Stores the scoring rubrics used by the model:

- `OUTDOOR_RUBRIC`
- `CLIMATE_RUBRIC`
- `ENERGY_RUBRIC`

Outdoor and energy are scored from 1 to 4. Climate is scored from 0 to 4.

### `src/scoring.py`

Builds the scoring prompt, calls the OpenAI Responses API, parses JSON, and attempts a model-based JSON repair if the first response is malformed.

Main functions:

- `build_prompt(...)`
- `call_model_json(...)`
- `repair_json_with_model(...)`

The prompt requires valid JSON with:

- section name
- score
- confidence
- reasoning
- evidence
- missing criteria for the next score

### `src/pipeline.py`

The original chunked scoring pipeline.

Workflow:

1. Load PDF.
2. Extract page text.
3. Create overlapping chunks.
4. Retrieve top chunks separately for outdoor, climate, and energy.
5. Score each section with the rubric.
6. Return section scores, total score, retrieved chunks, page count, and chunk count.

Use this when you want to reproduce the original chunked results.

### `src/pipeline_parent_context.py`

The newer parent-context scoring pipeline.

Workflow:

1. Load PDF.
2. Extract page text.
3. Create child chunks with larger parent spans.
4. Rank child chunks using weighted keyword retrieval.
5. Expand top child hits into merged parent contexts.
6. Score each section from the expanded evidence set.

This pipeline is intended to improve continuity and reduce missed context while keeping chunking deterministic.

### `src/run_score_fmps.py`

Batch runner for the original chunked pipeline. It contains the list of district FMPs and writes:

```text
data/output/all_fmps_chunked_results.csv
```

It also writes detailed JSON files locally, but those JSON files are ignored by Git.

## Data Files

### `data/pdfs/`

Local folder for source FMP PDFs.

This folder is ignored by Git because PDFs can be large and may have sharing restrictions. Company users should place FMP PDFs here locally before running the scorer.

### `data/output/all_fmps_chunked_results.csv`

Summary output from the original chunked pipeline.

Contains:

- district name
- PDF path
- predicted outdoor score
- predicted climate score
- predicted energy score
- predicted total score
- confidence labels
- reasoning fields
- page/chunk counts

### `data/output/parent_context_scores/all_fmps_parent_context_results.csv`

Summary output from the parent-context pipeline.

This is the newer scoring output format. Some rows may include an `error` column if a run failed due to API quota, disk space, or another runtime issue.

### Detailed JSON Outputs

Detailed JSON outputs may exist locally in `data/output/`, but they are ignored by Git. They can be useful for auditing retrieved evidence and model reasoning, but they are larger and not required for the shared repository.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git and should never be committed.

## Running the Original Chunked Pipeline

From the project root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/run_score_fmps.py
```

This scores all FMPs listed in `src/run_score_fmps.py` using the original chunking pipeline.

Primary output:

```text
data/output/all_fmps_chunked_results.csv
```

## Running One FMP With the Parent-Context Pipeline

Example:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -c "import json, sys; sys.path.insert(0, 'src'); from pipeline_parent_context import score_fmp_pdf; result = score_fmp_pdf('data/pdfs/MenloPark.pdf'); print(json.dumps(result, indent=2))"
```

This prints the full parent-context result for one PDF.

## Recommended Production Direction

The recommended pipeline direction is:

```text
PDF
-> deterministic page text extraction
-> child chunks for retrieval
-> weighted keyword retrieval
-> parent-context expansion
-> rubric-based LLM scoring
-> CSV summary outputs
```

This is preferred over LLM-first chunking because it is more consistent, reproducible, cheaper, and easier to debug across many district plans.

## Git and Privacy Notes

The following should not be committed:

- `.env`
- API keys
- `.venv/`
- source PDFs in `data/pdfs/`
- detailed JSON outputs
- experimental `src/FILE_*.py` scripts
- comparison-only scripts unless they are intentionally promoted

The `.gitignore` file is configured to keep these files local.

Before pushing, verify staged files with:

```bash
git diff --cached --name-only
```

And check for accidental API keys with:

```bash
git grep --cached -n "sk-\|OPENAI_API_KEY=.*[A-Za-z0-9_]" -- .
```

## Current Limitations

- The retrieval system is still keyword-based, though the parent-context version uses weights and bonuses.
- The model output depends on API availability and quota.
- Very large PDF runs can create large JSON files locally if detailed outputs are enabled.
- Some scores should be validated against human-coded examples before treating the system as final.

## Suggested Next Steps

1. Finish the parent-context run for any districts with errors.
2. Compare original chunked scores against parent-context scores.
3. Review changed scores manually, especially changes of 2 or more points in a category.
4. Add human-labeled benchmark scores for validation.
5. Tune keyword weights based on false positives and missed evidence.
