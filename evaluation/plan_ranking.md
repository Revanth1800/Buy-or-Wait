# Plan Ranking

The plan-ranking layer is deterministic. It accepts strict `CandidatePlanVerification` results and ranks only plans with `valid=True`. Invalid plans are ignored and cannot reach the selected-plan result.

## Ranking Order

The ranking key follows the problem statement exactly:

1. Complete the full request by `desired_completion_date`.
2. Require no spending changes.
3. Minimize `total_amount_paid`.
4. Start payment earlier.
5. Use fewer payments.
6. Use the lowest `payment_option_id`.

If all explicit rules are equal, the implementation keeps deterministic input order as a final stability tie-break.

## Ranking Attributes

Each ranked plan stores:

- `can_purchase_immediately`
- `completes_by_deadline`
- `preserves_safety_buffer`
- `requires_spending_changes`
- `total_cost`
- `waiting_duration_days`
- `number_of_payments`
- `amount_paid_immediately`
- `risk_or_uncertainty_count`
- `source_payment_option_id`

The risk or uncertainty count is recorded for audit visibility. It is not used ahead of the explicit problem-statement ranking rules.

## Ranking Result

Each selected plan stores:

- `ranking_key`
- `ranking_explanation`
- `competing_plans_considered`
- `reason_selected`

When no verified payable plan exists, `not_recommended` may be selected as the fallback.
