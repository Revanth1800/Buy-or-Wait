# Missing Amount Resolution

This layer resolves only missing financial-event amounts. It does not make buy-or-wait recommendations.

## Rules

- Start from normalized financial events.
- Only events whose normalized `amount` is `None` are considered.
- First look for `images.csv.related_event_id == financial_events.event_id`.
- If no linked image exists, leave the event unresolved.
- If a linked image exists, use image interpretation only for that missing amount.
- Never invent an amount. If the image is cropped, unclear, or has multiple plausible final values, mark the evidence `ambiguous`.
- Preserve the original raw amount and record the evidence source, method, confidence, status, and notes.
- Do not mutate the original normalized event; later decision logic can join by `record_id`.

## Evidence Structure

Each `AmountResolutionEvidence` has:

- `record_id`
- `original_value`
- `resolved_value`
- `evidence_source`
- `resolution_method`
- `confidence`
- `status`: `resolved`, `unresolved`, or `ambiguous`
- `notes`

## Current Image Evidence

The 16 missing amounts in the supplied dataset all have linked image records. Manual image review produced 15 resolved amounts and 1 ambiguous amount.

| Event ID | Image | Status | Resolved amount | Method | Notes |
|---|---|---:|---:|---|---|
| `event_253` | `image_01.png` | `resolved` | `4365000` | `manual_image_review:net_pay` | Payslip net pay. |
| `event_1442` | `image_02.png` | `resolved` | `100000` | `manual_image_review:balance_due` | Linked event is outstanding rent balance; receipt has several rent totals. |
| `event_1545` | `image_03.png` | `resolved` | `41272.00` | `manual_image_review:net_amount` | Grocery receipt net amount / cash paid. |
| `event_1700` | `image_04.png` | `ambiguous` |  | `manual_image_review:cropped_receipt` | Visible item bill is INR 2,854.00, but final billing section is cropped. |
| `event_1786` | `image_05.png` | `resolved` | `704.05` | `manual_image_review:amount_due` | Telecom amount due / charge total. |
| `event_3051` | `image_06.png` | `resolved` | `1995.00` | `manual_image_review:invoice_total` | Grocery invoice total. |
| `event_3231` | `image_07.png` | `resolved` | `8528` | `manual_image_review:grand_total` | Restaurant grand total. |
| `event_4535` | `image_08.png` | `resolved` | `15339.00` | `manual_image_review:total_amount_received` | Maintenance receipt total received. |
| `event_5170` | `image_09.png` | `resolved` | `723.00` | `manual_image_review:total_amount_received` | Water bill receipt total received. |
| `event_6033` | `image_10.png` | `resolved` | `79679.26` | `manual_image_review:balance_due` | Grocery invoice total / balance due. |
| `event_6859` | `image_11.png` | `resolved` | `3650.00` | `manual_image_review:amount_payable` | Hospital amount payable. |
| `event_7307` | `image_12.png` | `resolved` | `33.50` | `manual_image_review:fare_total` | Taxi fare total; cash paid includes change. |
| `event_7941` | `image_13.png` | `resolved` | `2298` | `manual_image_review:total_paid` | Shopping total paid. |
| `event_9421` | `image_14.png` | `resolved` | `4543.00` | `manual_image_review:handwritten_total` | Handwritten pharmacy total; lower confidence. |
| `event_9806` | `image_15.png` | `resolved` | `9968.00` | `manual_image_review:grand_total` | Airline invoice grand total. |
| `event_10521` | `image_16.png` | `resolved` | `393.22` | `manual_image_review:invoice_total` | EV charging invoice total. |

