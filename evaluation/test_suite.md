# Test Suite

The test suite is deterministic and does not require live external services.

## Run All Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

You can also run the current focused test module directly:

```bash
python -m unittest tests.test_normalization
```

On systems where `python3` is available:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Coverage Areas

Unit tests cover:

- Date parsing
- Currency conversion
- Duplicate detection
- Transaction filtering
- Missing-value handling
- Financial-state reconstruction
- Recurring-income detection
- Recurring-expense detection
- 90-day forecasting
- Safety-buffer calculations
- Earliest safe payment date
- Full-payment plans
- Partial-payment plans
- Installment plans
- Unsafe plans
- Plan verification
- Plan ranking
- Output validation

Integration tests create a complete small dataset in a temporary directory and run the full pipeline from loading through validated `output.csv` generation.
