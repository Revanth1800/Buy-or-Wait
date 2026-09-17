# Buy or Wait?

Deterministic solution for the HackerRank Orchestrate "Buy or Wait?" challenge. The program reads the supplied financial datasets, reconstructs each user's financial state, forecasts cash flow for 90 days, generates safe payment plans, verifies and ranks them, then writes one recommendation per request to root-level `output.csv`.

## Project Overview

For each row in `dataset/requests.csv`, the solution decides whether the user should:

- pay in full
- pay partially
- use a supplied installment option
- wait until a later safe date
- not proceed

The recommendation must keep the user's projected balance above `minimum_balance_to_keep`, reserve pending debits, avoid counting uncertain income, ignore failed/cancelled/duplicate events, and avoid treating unrealized investments as available cash.

## Architecture

The main implementation is in `code/main.py`. The code is organized as reusable stages:

- Dataset loading and validation
- Normalization into typed records
- Missing-amount and image-evidence resolution
- Financial-state reconstruction
- 90-day cash-flow forecasting
- Safe-payment calculation
- Candidate-plan generation
- Strict candidate verification
- Deterministic plan ranking
- Final decision generation
- Output-file validation and report writing

Supporting documentation lives in `evaluation/`.

## Data-Processing Flow

The default pipeline runs in this order:

1. Load raw datasets from `dataset/`.
2. Normalize input data.
3. Resolve missing values and image-based evidence.
4. Reconstruct the financial state for each request.
5. Forecast the next 90 days.
6. Calculate the safe payment amount.
7. Calculate the earliest safe full-payment date.
8. Generate candidate plans.
9. Verify candidate plans.
10. Rank valid plans.
11. Generate the final decision.
12. Validate the output schema and recommendation support.
13. Write root-level `output.csv`.

The final output columns are:

```text
request_id,amount_safe_to_pay,affordability_status,recommended_payment_method,payment_plan,earliest_date_for_full_payment,spending_changes_needed,decision_explanation
```

## How To Run

Required challenge command:

```bash
python3 code/main.py
```

On this Windows development machine, `python3.exe` resolved to an inaccessible Microsoft app execution alias, so the verified local command was:

```bash
python code/main.py
```

Successful execution writes:

- `output.csv`
- `evaluation/output_validation_report.md`

Useful diagnostics:

```bash
python code/main.py --diagnose
python code/main.py --normalize-diagnose
python code/main.py --resolve-missing-diagnose
python code/main.py --state-diagnose
python code/main.py --forecast-diagnose
python code/main.py --safe-payment-diagnose
python code/main.py --candidate-plan-diagnose
python code/main.py --verify-plan-diagnose
python code/main.py --rank-plan-diagnose
```

## How To Run Tests

Use explicit discovery:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Or run the current focused module:

```bash
python -m unittest tests.test_normalization
```

The suite is deterministic and does not call live external services.

## AI Usage

The financial pipeline is deterministic. AI is not used for:

- final balance calculations
- currency conversion arithmetic
- forecast arithmetic
- safety-buffer calculations
- installment arithmetic
- candidate validation
- final plan ranking
- writing arbitrary output values

The code includes an optional structured AI-assistance adapter for tasks that genuinely require language or image interpretation. In the final full-dataset run, no runtime AI client was configured and no AI calls were made by the program. Missing image amounts were resolved using recorded evidence in code, with one ambiguous image preserved as ambiguous rather than guessed.

Development used Codex as a coding assistant. See `log.txt` for the conversation transcript required by the repo instructions.

## Assumptions

- `dataset/requests.csv` is the source of evaluation requests.
- `dataset/output.csv` is only a blank template; root-level `output.csv` is the generated prediction file.
- All request amounts and payment options are already in the user's home currency.
- Foreign-currency financial events use exact supplied dated rates from `exchange_rates.csv`.
- Pending debits are reserved; pending credits are tracked as uncertain until settled.
- Recurrence is inferred only from repeated settled historical records with matching category and normalized description.
- Spending-change recommendations are currently not generated; `spending_changes_needed` is `none`.

## Limitations

- The implementation does not use live banking, market-data, or exchange-rate APIs.
- The optional AI adapter is provider-agnostic and not connected to a live model by default.
- Image evidence is based on recorded interpretations for the supplied dataset.
- Same-day payment checks are conservative and do not assume income arrives before a purchase on the same date.
- Output quality depends on the challenge datasets and the implemented deterministic rules.

## Validation Status

The latest local run processed 250 requests, wrote root-level `output.csv`, and produced `evaluation/output_validation_report.md` with 1667 checks passed and 0 failed.
