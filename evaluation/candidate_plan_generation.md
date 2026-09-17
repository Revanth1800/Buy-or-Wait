# Candidate-Plan Generation

This layer generates valid candidate plans for later ranking. It does not rank plans, choose recommendations, or write `output.csv`.

## Inputs

- Normalized `UserRequest` records.
- Request-scoped `FinancialState` records.
- Request-scoped 90-day `CashFlowForecast` records.
- `SafePaymentCalculation` records.
- Normalized `PaymentOption` records from `request_payment_options.csv`.

## Output Structure

Each `CandidatePlan` contains:

- `request_id`
- `plan_type`: `full_payment`, `partial_payment`, `installments`, `wait`, or `not_recommended`
- `amount_paid_immediately`
- `remaining_amount`
- `payment_dates`
- `number_of_installments`
- `installment_amounts`
- `total_amount_paid`
- `fees_or_additional_costs`
- `projected_balance_after_each_payment`
- `preserves_safety_buffer`
- `follows_spending_change_restrictions`
- `is_valid`
- `payment_plan`
- `source_payment_option_id`
- `rejection_reasons`
- `explanation`

Each `PlanPayment` contains:

- `payment_date`
- `amount`
- `projected_balance_after_payment`

## Generated Plan Types

- `full_payment`: one payment for the request amount on `request_date`.
- `partial_payment`: two payments, using the safe immediate amount on `request_date` and the remaining amount on `earliest_date_for_full_payment`.
- `installments`: follows a supplied installment payment option exactly.
- `wait`: one full payment on a later safe full-payment date.
- `not_recommended`: fallback candidate only when no valid payable candidate exists.

## Rejection Rules

Invalid candidates are not returned by the public `generate_candidate_plans` function, except the fallback `not_recommended` candidate when no payable candidate is valid.

Candidates are rejected when:

- The user does not consider the required payment method.
- A full payment exceeds the safe immediate amount.
- A partial payment is not allowed by the request.
- A partial payment does not have `0 < amount_safe_to_pay < requested_amount`.
- A partial payment has no safe later date for the remaining amount.
- A plan completes after `desired_completion_date`.
- A wait plan does not have a later safe full-payment date.
- An installment option is malformed.
- An installment option is missing its payment frequency for multiple payments.
- An installment option exceeds the user's `max_installment_months`.
- The generated installment schedule total does not match the supplied `total_payable_amount`.
- Any payment is non-positive.
- Any payment date falls outside the 90-day forecast.
- The plan would push any forecast opening or closing balance below the required buffer after accounting for cumulative plan payments.

## Spending Changes

This layer generates no-spending-change candidates only. Therefore `follows_spending_change_restrictions` is `True` for generated candidates. Spending-change candidate generation can be added later as a separate layer.

## Diagnostics

Run:

```powershell
python code\main.py --candidate-plan-diagnose
```

The diagnostic reports candidate counts by plan type and summarizes the first 10 request candidate sets.

