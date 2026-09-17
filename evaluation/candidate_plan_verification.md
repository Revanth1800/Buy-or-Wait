# Candidate-Plan Verification

The strict verification layer is the gate between candidate generation and any future ranking logic. It re-checks every generated candidate using the normalized request, reconstructed financial state, 90-day forecast, safe-payment calculation, and supplied payment options.

## Verification Rules

- `request_match`: the candidate must belong to the request being verified.
- `payment_dates_valid`: every payable plan must have at least one payment date inside the forecast horizon.
- `payment_dates_chronological`: payment dates must already be in chronological order.
- `payment_amounts_positive`: every scheduled payment must be greater than zero.
- `plan_fields_match_payment_plan`: summary fields must match the detailed `payment_plan`.
- `total_payment_matches_required_amount`: total paid must equal the requested amount plus fees.
- `enough_funds_on_payment_dates`: projected balance after each payment must be known and non-negative.
- `required_buffer_preserved`: the plan must preserve `minimum_balance_to_keep` after every forecast event and payment.
- `uncertain_income_not_guaranteed`: uncertain events must not affect guaranteed forecast balances.
- `spending_change_restrictions`: no unsupported spending behavior changes may be required.
- `upstream_fund_exclusions`: forecast events must come from the accepted forecast classes after excluding failed, cancelled, duplicate, and unrealized funds upstream.

## Plan-Specific Rules

- `full_payment`: one payment on `request_date`, equal to the requested amount, allowed by the user's payment preferences, and safe immediately.
- `partial_payment`: exactly two payments; the first equals the safe immediate amount on `request_date`, and the second pays the remainder on the earliest safe full-payment date no later than the desired completion date.
- `installments`: the plan must exactly match one supplied installment option, including dates, amounts, number of payments, financing fee, and total payable amount; it must also respect `max_installment_months`.
- `wait`: one full payment on the earliest later safe full-payment date, using full payment as an allowed method.
- `not_recommended`: no scheduled payments and zero total paid.

## Outputs

Each verification returns:

- `valid`
- `invalid_reason`
- `verification_details`

Future ranking should consume `verified_candidate_plans_for_ranking(...)`, which returns only plans whose strict verification passed.
