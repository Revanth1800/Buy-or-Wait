# 90-Day Financial Forecasting

This layer generates request-scoped cash-flow forecasts. It does not rank plans, recommend purchases, or write final predictions.

## Inputs

- `FinancialState` objects from the reconstruction layer.
- Confirmed income and upcoming obligations already converted into the user's home currency when possible.
- Recurring income and expense patterns inferred from settled historical cash events.
- Financial uncertainties from reconstruction and missing-information resolution.

## Output Structure

Each `CashFlowForecast` contains:

- `request_id`
- `user_id`
- `home_currency`
- `start_date`
- `horizon_days`
- `daily`
- `confirmed_events`
- `recurring_estimated_events`
- `uncertain_events`
- `audit_trail`

Each `DailyForecast` contains:

- `date`
- `opening_balance`
- `expected_income`
- `expected_expenses`
- `net_change`
- `closing_balance`
- `events`

Each `ForecastEvent` contains:

- `event_id`
- `source_type`: `confirmed`, `recurring_estimated`, or `uncertain`
- `date`
- `direction`
- `category`
- `amount`
- `affects_balance`
- `explanation`

## Forecasting Rules

- Generate 90 daily rows starting on the request date.
- Start from `FinancialState.current_available_cash`.
- Carry the previous day's closing balance into the next day's opening balance.
- Confirmed future income increases the forecast balance on its settlement date.
- Confirmed future expenses and scheduled obligations decrease the forecast balance on their settlement date.
- Pending debits are treated as obligations when they are inside the forecast window.
- Pending credits are tracked as `uncertain` and do not affect projected balances.
- Financial uncertainties are listed as `uncertain` events and do not affect projected balances.
- Failed and cancelled events are already excluded by the reconstruction layer.
- Unrealized investments and non-cash investment values are not included as available cash.
- Amounts use home-currency values produced by the reconstruction layer.
- Missing exchange rates or unreliable missing-amount evidence prevent the affected event from moving the balance.

## Recurrence Rules

- Recurring income is inferred from two or more settled historical credit events with the same category and normalized description.
- Recurring expenses are inferred from two or more settled historical debit events with the same category and normalized description.
- Recurring estimates use the last observed home-currency amount.
- Recurring estimates repeat every 30 days from the last observed event date.
- Recurring estimates are marked `recurring_estimated`, not `confirmed`.
- The forecast does not use uncertain income as guaranteed recurring income.

## Diagnostics

Run:

```powershell
python code\main.py --forecast-diagnose
```

The diagnostic reports the number of forecasts, daily row count, confirmed event count, recurring estimated event count, uncertain event count, and minimum closing balance for the first 10 request forecasts.

