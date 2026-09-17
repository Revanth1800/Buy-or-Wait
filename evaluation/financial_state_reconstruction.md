# Financial-State Reconstruction

This layer builds request-scoped financial-state objects. It prepares the facts needed by later planning logic, but it does not rank plans, recommend payment methods, or generate `output.csv`.

## Inputs

- Normalized accounts, requests, financial events, and exchange rates.
- Optional missing-amount resolution evidence from `resolve_missing_amounts`.

## Output Structure

Each `FinancialState` contains:

- `request_id`, `user_id`, `request_date`, and `home_currency`
- `current_available_cash`
- `account_balances`
- `minimum_balance_to_keep`
- `pending_credits`
- `pending_debits`
- `confirmed_income`
- `confirmed_expenses`
- `recurring_income`
- `recurring_expenses`
- `upcoming_obligations`
- `investments`
- `recent_spending_history`
- `uncertainties`
- `audit_trail`

## Reconstruction Rules

- Start every request from `financial_profiles.current_available_balance`.
- Preserve `minimum_balance_to_keep` for later affordability checks.
- Reconstruct only records for the request's `user_id`.
- Exclude `failed` and `cancelled` events from cash-flow buckets.
- Track duplicate event IDs and skip repeated IDs if encountered.
- Record `pending` credits but do not count them as confirmed available money.
- Record `pending` debits and include them as upcoming obligations when their relevant date is inside the 90-day forecast window.
- Treat `settled` and `scheduled` credits inside the 90-day forecast window as confirmed income.
- Use settled historical credits as recurring-income candidates.
- Treat `settled` debits in the previous 90 days as confirmed expenses and recent spending history.
- Treat `settled` or `scheduled` debits inside the 90-day forecast window as upcoming obligations.
- Record investments separately.
- Do not treat `unrealized` investment values or `non_cash` records as immediately available cash.
- Use resolved image evidence only when the missing-amount layer marks the record as `resolved`.
- Preserve unresolved or ambiguous missing amounts in `uncertainties`.
- Add audit-trail entries explaining starting balances and every major inclusion or exclusion.

## Currency Conversion

- If an event currency equals the user's home currency, no exchange-rate lookup is required.
- If an event currency differs from home currency, use the supplied exchange rate for `(conversion_date, from_currency, home_currency)`.
- The conversion date is `settlement_date` when present, otherwise `event_date`.
- Missing conversion dates or missing exact supplied rates are preserved as financial uncertainty.
- This layer does not infer inverse rates or use live exchange rates.

## Recurring Expense Detection

- Recurring income candidates are inferred from settled credit history only.
- Recurring expense candidates are inferred from settled debit history only.
- Events are grouped by category and normalized description.
- A group with two or more observed settled credit events becomes a `RecurringIncome`.
- A group with two or more observed settled debit events becomes a `RecurringExpense`.
- This is only a conservative reconstruction signal; later forecasting logic may choose how to project it.

## Diagnostics

Run:

```powershell
python code\main.py --state-diagnose
```

The diagnostic reports how many request states were reconstructed, total uncertainties, and summary bucket counts for the first 10 request states.
