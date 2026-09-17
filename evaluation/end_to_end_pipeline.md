# End-To-End Pipeline

The default entry point runs the complete deterministic pipeline:

```bash
python3 code/main.py
```

On systems where `python3` is not available, the same script can be run with the available Python 3 interpreter.

## Stage Order

1. Load raw datasets from `dataset/`.
2. Normalize input data.
3. Resolve missing values and image-based evidence.
4. Reconstruct financial state per request.
5. Forecast the next 90 days.
6. Calculate the safe payment amount.
7. Calculate the earliest safe full-payment date.
8. Generate candidate plans.
9. Verify candidate plans.
10. Rank valid plans.
11. Generate the final decision.
12. Validate the output schema and allowed values.
13. Write root-level `output.csv`.

## Output

The generated CSV uses exactly:

```text
request_id,amount_safe_to_pay,affordability_status,recommended_payment_method,payment_plan,earliest_date_for_full_payment,spending_changes_needed,decision_explanation
```

The pipeline writes one row for every request in `dataset/requests.csv`.
