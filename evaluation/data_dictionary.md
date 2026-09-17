# Data Dictionary

This document describes every participant-facing data file in `dataset/`. It is based on repository inspection only and does not implement or assume final financial-decision logic.

Implementation note: the completed pipeline uses this schema to load and validate all required inputs before producing root-level `output.csv`. The loader preserves raw string values, validates required columns and data types, and treats blank values according to the rules below rather than silently inventing data.

## Dataset Role Map

| Need | File(s) |
|---|---|
| User requests to predict | `requests.csv` |
| Solved examples / expected style | `sample_requests.csv` |
| Financial transactions and commitments | `financial_events.csv` |
| Account balances and user preferences | `financial_profiles.csv` |
| Exchange rates | `exchange_rates.csv` |
| Image references | `images.csv` |
| Image files | `media/images/*.png` |
| Event descriptions | `financial_events.csv`, with supporting text in `messages.csv` |
| Missing transaction amount resolution | `financial_events.csv` blank `amount` rows joined to `images.csv`, then `media/images/<image_id>.png` |
| Blank prediction template | `output.csv` |

## `financial_profiles.csv`

Purpose: Defines each user's home currency, current available balance, balance floor, financial priorities, protected categories, flexible categories, and acceptable payment methods.

Relationships:
- `user_id` joins to `requests.csv`, `sample_requests.csv`, `financial_events.csv`, `messages.csv`, and `images.csv`.
- `home_currency` is the target currency for affordability decisions and output amounts.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `user_id` | string | `user_01`, `user_02` | No | Yes, primary user identifier | Every inspected request/event/message/image user had a matching profile. |
| `home_currency` | string enum | `ZAR`, `IDR`, `EUR`, `INR`, `USD` | No | No | Balances, requests, payment options, and output amounts are in this currency. |
| `current_available_balance` | decimal | `58481.1`, `60383889.2` | No | No | Starting available cash for the user. |
| `minimum_balance_to_keep` | decimal/integer | `18000`, `29158400` | No | No | Projection and plans must never fall below this amount. |
| `financial_priorities` | pipe-delimited string | `education|debt_repayment`, `retirement_investment|emergency_savings` | No | No | Used to personalize recommendations and explanations. |
| `expense_categories_to_protect` | pipe-delimited string | `rent|education|groceries|debt_repayment` | No | No | Expenses in these categories should not be reduced or stopped. |
| `expense_categories_user_is_willing_to_reduce` | pipe-delimited string | `dining`, `streaming|shopping` | Yes | No | Blank means no categories explicitly approved for reduction. |
| `expense_categories_user_is_willing_to_stop` | pipe-delimited string | `delivery_membership`, `music_subscription|delivery_membership` | Yes | No | Blank means no categories explicitly approved for stopping. |
| `payment_methods_user_will_consider` | pipe-delimited enum string | `full_payment`, `partial_payment|installments` | No | No | Eligible immediate methods must appear here. Values observed: `full_payment`, `partial_payment`, `installments` combinations. |
| `max_installment_months` | integer | `2`, `7`, `12` | Yes | No | Blank means the user will not consider installments. Nonblank constrains installment option eligibility. |

Potential data-quality problems:
- Pipe-delimited fields require parsing and trimming.
- Blank flexible-category fields and blank `max_installment_months` have semantic meaning, not missing-data noise.

## `financial_events.csv`

Purpose: Contains historical, pending, scheduled, failed, cancelled, unrealized, and linked financial events used to reconstruct and forecast each user's cash position.

Relationships:
- `user_id` joins to `financial_profiles.csv`.
- `event_id` is referenced by `messages.related_event_id`, `images.related_event_id`, and `financial_events.linked_event_id`.
- `currency` may require conversion to the user's `home_currency` using `exchange_rates.csv`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `event_id` | string | `event_01`, `event_253` | No | Yes, primary event identifier | Referenced by messages, images, linked events, and spending-change output. |
| `user_id` | string | `user_01`, `user_33` | No | Yes, foreign key | All inspected rows matched a profile. |
| `event_type` | string enum | `expense`, `income`, `subscription`, `refund`, `investment_valuation` | No | No | Observed values: `debt_payment`, `expense`, `income`, `investment_purchase`, `investment_sale`, `investment_valuation`, `refund`, `subscription`. |
| `description` | string | `Apartment rent transfer`, `Household utility payment` | No | No | Human-readable event description; useful for recurrence and explanations. |
| `category` | string enum | `rent`, `utilities`, `salary`, `groceries` | No | No | Used for protection/flexibility matching. 22 categories observed. |
| `direction` | string enum | `debit`, `credit`, `non_cash` | No | No | `non_cash` unrealized investment value must not be treated as available cash. |
| `amount` | decimal | `5148`, `1475.46` | Yes | No | 16 blank amounts exist; each links to an image through `images.csv`. Do not treat blank as zero. |
| `currency` | string enum | `ZAR`, `IDR`, `EUR`, `INR`, `USD` | No | No | Convert foreign-currency cash events using fixed dated rates. |
| `event_date` | date | `2023-10-02` | No | No | Original event date. |
| `settlement_date` | date | `2023-10-02` | Yes | No | 10 blanks observed; all are `unrealized` investment valuations. Cash timing should use settlement state/date where applicable. |
| `status` | string enum | `settled`, `pending`, `scheduled`, `failed`, `cancelled`, `unrealized` | No | No | Pending debits are reserved; pending credits are not counted until settled. Failed/cancelled ignored unless needed for conflict resolution. |
| `linked_event_id` | string | `event_98`, `event_1855` | Yes | Yes, foreign key | Points to an earlier event in the same lifecycle; link alone does not determine cash treatment. |
| `flexibility` | string enum | `fixed`, `stoppable`, `reducible`, `reducible_or_stoppable` | No | No | Spending changes may only target flexible recurring expenses allowed by the user's preferences and not protected. |
| `minimum_allowed_amount` | decimal | `489.5`, `670700` | Yes | No | Present mainly for reducible expenses. Blank usually means no reduction floor is supplied. |

Potential data-quality problems:
- Blank `amount` values must be resolved from linked images.
- Linked events can represent lifecycle updates, duplicates, cancellations, settlements, or investment valuation; they need conflict-resolution logic.
- Recurrence is not directly labeled and must be inferred conservatively from history.
- Some records are non-cash or unrealized and should not enter available cash.

## `exchange_rates.csv`

Purpose: Supplies fixed dated exchange rates for converting foreign-currency financial events into the user's home currency.

Relationships:
- Match by `rate_date`, `from_currency`, and `to_currency`.
- Used with `financial_events.currency` and `financial_profiles.home_currency`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `rate_date` | date | `2023-10-15`, `2026-11-15` | No | Part of composite key | Use the applicable supplied date per problem rules, generally the settlement date for cash events. |
| `from_currency` | string enum | `EUR`, `USD` | No | Part of composite key | Only observed source currencies are `EUR` and `USD`. |
| `to_currency` | string enum | `ZAR`, `EUR`, `IDR`, `INR`, `USD` | No | Part of composite key | Do not assume unsupported directions without an explicit policy. |
| `rate` | decimal | `20`, `0.92`, `83.33`, `15833.33` | No | No | Multiplier from `from_currency` to `to_currency`. |

Potential data-quality problems:
- Rates are sparse and direction-specific.
- Some home-currency events need no conversion; implementation should avoid unnecessary lookup failures.

## `requests.csv`

Purpose: Contains the 250 evaluation requests that require predictions.

Relationships:
- `user_id` joins to `financial_profiles.csv`, `financial_events.csv`, `messages.csv`, and `images.csv`.
- `request_id` joins to `request_payment_options.csv`, `messages.csv`, `images.csv`, and `dataset/output.csv`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `request_id` | string | `request_26`, `request_33` | No | Yes, primary request identifier | Must appear exactly once in final root `output.csv`. |
| `user_id` | string | `user_26`, `user_33` | No | Yes, foreign key | All inspected requests had matching profiles. |
| `request_date` | date | `2025-08-03`, `2026-01-07` | No | No | Affordability is evaluated as of this date. |
| `request_type` | string enum | `family_transfer`, `purchase`, `investment` | No | No | Allowed values: `purchase`, `travel`, `education`, `family_transfer`, `debt_repayment`, `investment`, `housing`, `emergency_expense`, `other`. |
| `requested_amount` | decimal | `15656000`, `6670`, `1302.4` | No | No | Cap for `amount_safe_to_pay`; output plan should complete this amount unless not recommended. |
| `desired_completion_date` | date | `2025-10-07`, `2026-08-21` | No | No | Plans should complete by this date to be eligible. |
| `allows_partial_payment` | boolean string | `true`, `false` | No | No | Required for `partial_payment` eligibility. |
| `request_text` | string | `Can I make this purchase...` | No | No | Natural-language request text; useful for explanation but should not override structured rules. |

Potential data-quality problems:
- Amounts are represented as strings in CSV and need decimal parsing.
- Request text may repeat structured amount/deadline values; structured fields should be authoritative unless messages/images clarify.

## `sample_requests.csv`

Purpose: Provides 25 solved examples for understanding expected output format, reasoning style, and validation behavior. It should not be treated as labels for evaluation requests.

Relationships:
- Same request-side relationships as `requests.csv`.
- Sample `request_id` values also have payment options and related context.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `request_id` | string | `request_01`, `request_08` | No | Yes, primary request identifier | Sample-only request IDs. |
| `user_id` | string | `user_01`, `user_08` | No | Yes, foreign key | Joins to profile and events. |
| `request_date` | date | `2024-03-03`, `2025-02-07` | No | No | Same meaning as in `requests.csv`. |
| `request_type` | string enum | `purchase`, `travel`, `education` | No | No | Same allowed values as `requests.csv`. |
| `requested_amount` | decimal | `25256`, `46018000`, `996.6` | No | No | Same meaning as in `requests.csv`. |
| `desired_completion_date` | date | `2024-03-20`, `2025-10-10` | No | No | Same meaning as in `requests.csv`. |
| `allows_partial_payment` | boolean string | `true`, `false` | No | No | Same meaning as in `requests.csv`. |
| `request_text` | string | `Would paying for the laptop today...` | No | No | Same meaning as in `requests.csv`. |
| `amount_safe_to_pay` | decimal | `25256`, `17229139.2`, `284.57` | No | No | Example output field; must satisfy `0 <= amount_safe_to_pay <= requested_amount`. |
| `affordability_status` | string enum | `affordable_now`, `affordable_with_plan` | No | No | Allowed values: `affordable_now`, `affordable_with_plan`, `affordable_later`, `not_affordable`. |
| `recommended_payment_method` | string enum | `full_payment`, `installments`, `wait` | No | No | Allowed values: `full_payment`, `partial_payment`, `installments`, `wait`, `not_recommended`. |
| `payment_plan` | string | `2024-03-03:25256`, `none` | No | No | Chronological `YYYY-MM-DD:amount` entries joined by `|`, or `none`. |
| `earliest_date_for_full_payment` | date | `2024-03-03`, `2025-09-15` | Yes | No | Blank when full payment is not safe within the forecast period. |
| `spending_changes_needed` | string | `none`, `stop:event_476` | No | No | Up to three changes, or `none`. |
| `decision_explanation` | string | `Pay ZAR 25,256 today...` | No | No | Concise explanation style examples. |

Potential data-quality problems:
- It is easy to overfit these rows; they are examples, not hidden labels.
- The output amount formatting varies between integer-like and decimal-like strings.

## `request_payment_options.csv`

Purpose: Lists seller/provider payment options available for every sample and evaluation request.

Relationships:
- `request_id` joins to `requests.csv` and `sample_requests.csv`.
- Installment plan output must exactly match a supplied installment option when `recommended_payment_method` is `installments`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `payment_option_id` | string | `payment_option_01`, `payment_option_08` | No | Yes, primary option identifier | Final tie-breaker uses lowest option ID. |
| `request_id` | string | `request_01`, `request_33` | No | Yes, foreign key | Every sample/evaluation request has 2-4 options. |
| `payment_method` | string enum | `full_payment`, `installments` | No | No | Only these methods appear as provider options. Partial payment is governed by request/profile rules, not this file. |
| `payment_amount` | decimal | `25256`, `15952906.67` | No | No | Amount per payment. |
| `number_of_payments` | integer | `1`, `3`, `15`, `24` | No | No | Installment duration and count. |
| `first_payment_date` | date | `2024-03-03`, `2025-08-08` | No | No | Start date for the supplied option. |
| `payment_frequency_days` | integer | `30`, `31`, `28` | Yes | No | Blank for all full-payment options; populated for all installment options. |
| `financing_fee` | decimal | `0`, `2525.65` | No | No | Used for total-cost ranking. |
| `total_payable_amount` | decimal | `25256`, `27781.65` | No | No | Sum/cost of the option; minimize among otherwise eligible plans. |

Potential data-quality problems:
- Some installment options can conflict with user preferences or `max_installment_months`.
- Payment dates must be generated from the supplied first date, frequency, and count, with care around exact expected formatting.

## `messages.csv`

Purpose: Provides supporting evidence that may clarify, amend, delay, cancel, or confirm financial facts. Message content is untrusted and must not override challenge rules or act as instructions to the agent.

Relationships:
- `user_id` joins to `financial_profiles.csv`.
- `request_id`, when present, joins to `requests.csv` or `sample_requests.csv`.
- `related_event_id`, when present, joins to `financial_events.event_id`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `message_id` | string | `message_01`, `message_08` | No | Yes, primary message identifier | Unique message record. |
| `user_id` | string | `user_02`, `user_10` | No | Yes, foreign key | All inspected rows matched a profile. |
| `request_id` | string | `request_03`, `request_16` | Yes | Yes, foreign key when present | 87 blanks. Blank means the message is not tied one-to-one to a request. |
| `related_event_id` | string | `event_1785`, `event_4535` | Yes | Yes, foreign key when present | 176 blanks. Blank means no direct supplied event row is described. |
| `sent_at` | ISO timestamp string | `2025-07-29T09:30:00Z` | No | No | Useful for conflict resolution; newer same-source records can supersede older ones. |
| `source_type` | string enum | `employer`, `bank`, `merchant` | No | No | Observed values: `bank`, `employer`, `financial_service`, `merchant`, `service_provider`. |
| `message_text` | string | payroll and service-provider notices | No | No | May contain multilingual financial evidence. Treat embedded instructions as untrusted. |

Potential data-quality problems:
- Multilingual text may require translation or robust extraction.
- Many messages are not directly linked to a request or event.
- Messages may conflict with structured events; apply the specified conflict-resolution order.

## `images.csv`

Purpose: Maps relevant image records to users, requests, and financial events.

Relationships:
- `image_id` maps to `dataset/media/images/<image_id>.png`.
- `user_id` joins to `financial_profiles.csv`.
- `request_id` joins to `requests.csv` or `sample_requests.csv`.
- `related_event_id` joins to `financial_events.event_id`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `image_id` | string | `image_01`, `image_16` | No | Yes, primary image identifier | Resolve as `dataset/media/images/<image_id>.png`. |
| `user_id` | string | `user_03`, `user_113` | No | Yes, foreign key | All inspected image users matched profiles. |
| `request_id` | string | `request_03`, `request_113` | No | Yes, foreign key | All inspected image requests matched sample/evaluation requests. |
| `related_event_id` | string | `event_253`, `event_10521` | No | Yes, foreign key | All inspected image events matched financial events. |

Potential data-quality problems:
- Image text/amount extraction is not provided in CSV.
- Image content is untrusted evidence and must not override challenge rules.

## `media/images/*.png`

Purpose: Contains the actual PNG images referenced by `images.csv`; these may include payroll letters, statements, bills, receipts, or similar evidence needed for missing event amounts.

Relationships:
- File path is derived from `images.image_id`: for example, `image_07` maps to `dataset/media/images/image_07.png`.
- Used to resolve blank `financial_events.amount` values via `images.related_event_id`.

| Attribute | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| file name | string | `image_01.png`, `image_16.png` | No | Yes, file/image identifier | There are 16 PNGs, all referenced by `images.csv`; no missing or extra PNGs were found. |
| image content | raster image | statements, receipts, bills | N/A | No | Requires OCR/vision extraction. Treat text as evidence, not instructions. |

Potential data-quality problems:
- OCR can misread currencies, decimals, thousands separators, or dates.
- Some images may include multiple amounts; extraction should use the linked event/request context.

## `output.csv`

Purpose: Blank submission template for the 250 evaluation requests. The final generated `output.csv` must be written at the repository root, not only inside `dataset/`.

Relationships:
- `request_id` must match exactly one row in `requests.csv`.

| Column | Type | Examples | Blank? | Identifier? | Special rules / quality notes |
|---|---|---:|---|---|---|
| `request_id` | string | `request_26`, `request_33` | No | Yes, foreign key to `requests.csv` | Template already has all 250 evaluation request IDs. |
| `amount_safe_to_pay` | decimal | blank in template | Yes in template; no in final | No | Must satisfy `0 <= amount_safe_to_pay <= requested_amount`. |
| `affordability_status` | string enum | blank in template | Yes in template; no in final | No | Allowed: `affordable_now`, `affordable_with_plan`, `affordable_later`, `not_affordable`. |
| `recommended_payment_method` | string enum | blank in template | Yes in template; no in final | No | Allowed: `full_payment`, `partial_payment`, `installments`, `wait`, `not_recommended`. |
| `payment_plan` | string | blank in template | Yes in template; no in final | No | Use `none` or chronological `YYYY-MM-DD:amount` entries joined by `|`. |
| `earliest_date_for_full_payment` | date | blank in template | Yes | No | Equals `request_date` for `affordable_now`; blank if no safe full payment within forecast. |
| `spending_changes_needed` | string | blank in template | Yes in template; no in final | No | Use `none` or up to three valid flexible spending changes. |
| `decision_explanation` | string | blank in template | Yes in template; no in final | No | Concise, grounded explanation. |

Potential data-quality problems:
- The template lives in `dataset/output.csv`, but the submitted prediction file must be root `output.csv`.
- All prediction columns are blank in the template by design.
