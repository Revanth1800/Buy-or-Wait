# Usage Report

This report describes the final full-dataset run that produced root-level `output.csv`.

## Run Summary

- Requests processed: 250
- Output rows written: 250
- Output validation: passed
- Validation checks: 1667 passed, 0 failed
- Runtime external services: none
- Runtime AI model calls: 0

## AI Models Or Tools Used

No AI model was called by `code/main.py` during the final full-dataset run.

Codex was used as a development assistant to inspect the repository, write code, run tests, and update documentation. That usage is recorded in `log.txt` as the chat transcript. Token usage for the development assistant is not available from the local project files.

## Purpose Of AI Calls

There were no runtime AI calls in the final pipeline run.

The code includes an optional structured AI-assistance adapter for future use on tasks that genuinely require language or image understanding:

- interpreting user messages
- extracting structured purchase details
- interpreting relevant images
- resolving ambiguous descriptions
- explaining evidence

The adapter is not responsible for financial arithmetic, candidate validation, ranking, or writing arbitrary output values.

## Approximate Token Usage

Runtime pipeline:

| Metric | Value |
|---|---:|
| Model calls | 0 |
| Input tokens | 0 |
| Output tokens | 0 |
| Total tokens | 0 |
| Average tokens per request | 0 |
| Estimated total model cost | 0 |
| Estimated model cost per request | 0 |

Development assistant token usage:

- Not available from this repository.
- See `log.txt` for the required development transcript.

## Fallback Behavior

Because no runtime AI client is configured by default, the pipeline uses deterministic evidence handling:

- Recorded image evidence resolves known linked missing amounts.
- Ambiguous image evidence remains ambiguous.
- Missing or low-confidence AI output would be marked unresolved or ambiguous if an AI client were provided.
- The financial pipeline never treats unresolved AI output as a confirmed amount.

## Limitations

- No live model, banking, market-data, or exchange-rate service is used at runtime.
- Runtime token and cost totals are zero because the final run is deterministic.
- Development-assistant token counts are not exposed in project artifacts.
