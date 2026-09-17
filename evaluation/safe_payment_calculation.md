# Safe-Payment Calculation

This layer calculates immediate safe payment capacity and the earliest safe full-payment date. It does not choose a payment method, rank plans, recommend purchases, or write `output.csv`.

## Inputs

- A normalized `UserRequest`
- The request's `FinancialState`
- The request's 90-day `CashFlowForecast`

## Output Structure

Each `SafePaymentCalculation` contains:

- `request_id`
- `purchase_price`
- `currency`
- `current_available_funds`
- `required_buffer`
- `minimum_projected_balance`
- `amount_safe_to_pay`
- `earliest_date_for_full_payment`
- `calculation_explanation`

## Rules

- The purchase price is `requests.requested_amount`, already expressed in the user's home currency by the dataset contract.
- Current available funds come from `FinancialState.current_available_cash`.
- The required buffer is `FinancialState.minimum_balance_to_keep`.
- The minimum projected balance is the minimum of all daily opening and closing balances in the 90-day forecast before adding the purchase.
- The immediate safe amount is:

```text
min(requested_amount, max(0, minimum_projected_balance - required_buffer))
```

- This prevents an immediate payment from pushing any forecasted opening or closing balance below the required buffer.
- Pending credits and uncertain events are not counted as guaranteed money because the forecast layer does not let them affect projected balances.
- Failed, cancelled, duplicate, and unrealized investment records are already excluded or separated by earlier layers.
- The earliest safe full-payment date is the first forecast date where subtracting the full purchase price from that date and every later forecast opening/closing balance still preserves the required buffer.
- Same-day timing is conservative: a payment on a date must be safe against that day's opening balance as well as its closing balance. This avoids assuming that income arrives before the purchase unless a later layer has stronger timing evidence.

## Diagnostics

Run:

```powershell
python code\main.py --safe-payment-diagnose
```

The diagnostic reports generated calculations and shows safe-now amount, purchase price, minimum projected balance, required buffer, and earliest full-payment date for the first 10 requests.

