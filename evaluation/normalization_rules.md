# Normalization Rules

This document records the current data-normalization layer. These rules prepare data for later stages only; they do not decide whether a user should buy or wait.

## General Rules

- Preserve source evidence: every normalized record carries `raw_source`, a dictionary of original CSV string values after basic loader trimming.
- Avoid invention: blank or invalid values normalize to `None` or an empty tuple and are recorded as `NormalizationIssue` when the missing value is uncertain or invalid.
- Keep raw and normalized data separate: normalized dataclasses do not replace the loaded CSV rows.
- Treat normalization issues as signals for later evidence handling, not as automatic decision outcomes.

## Dates

- Date values normalize to `datetime.date`.
- Supported input formats are `YYYY-MM-DD`, `YYYY/MM/DD`, `DD-MM-YYYY`, `DD/MM/YYYY`, and `MM/DD/YYYY`.
- Invalid dates normalize to `None` and add an `invalid_date` issue.
- Blank required dates normalize to `None` and add a `blank` issue.
- Blank optional dates, such as an absent `settlement_date`, normalize to `None` without an issue.
- The loader still validates official dataset date columns against the schema before normalization.

## Date-Times

- Loader date-time parsing accepts ISO-8601 values.
- A trailing `Z` is normalized to `+00:00` before parsing.
- Normalized domain records currently retain message text only indirectly through loaded tables; message-specific normalized structures can be added later if needed.

## Currency Codes

- Currency codes are stripped and uppercased.
- Valid normalized currency codes must match three uppercase letters, for example `USD`, `EUR`, `INR`, `IDR`, or `ZAR`.
- Blank currencies normalize to `None` with a `blank` issue.
- Non-three-letter currency values normalize to `None` with an `invalid_currency` issue.
- The normalizer does not convert money between currencies. Exchange conversion belongs to later financial-state logic.

## Numeric Amounts

- Numeric values normalize to `Decimal`.
- Commas are removed before decimal parsing, so `1,234.50` becomes `Decimal("1234.50")`.
- Blank decimal fields normalize to `None`.
- Invalid decimal values normalize to `None` with an `invalid_decimal` issue.
- Integer fields parse through `Decimal` first and must have no fractional part.
- Invalid integer values normalize to `None` with an `invalid_integer` issue.

## Booleans

- Boolean values normalize to Python `bool`.
- Accepted true values: `true`, `t`, `yes`, `y`, `1`.
- Accepted false values: `false`, `f`, `no`, `n`, `0`.
- Blank values normalize to `None` with a `blank` issue.
- Other values normalize to `None` with an `invalid_boolean` issue.

## Identifiers

- Identifiers are stripped and lowercased.
- This applies to user, request, event, image, linked-event, and payment-option identifiers.
- Blank required identifiers normalize to `None` with a `blank` issue.
- Blank optional identifiers, such as an absent `linked_event_id`, normalize to `None` without an issue.
- There is no separate account identifier in the supplied data, so the `Account` structure uses normalized `user_id` as the account-level identifier.

## Tokens And Enumerated Text

- Token-like values are stripped and lowercased.
- Event type aliases are normalized where obvious, for example `debt payment` and `debt-payment` become `debt_payment`.
- Status aliases are normalized where obvious, for example `completed`, `complete`, and `posted` become `settled`; `canceled` becomes `cancelled`.
- Unknown token values are preserved in normalized lowercase form instead of being invented or mapped to a guessed value.

## Pipe-Delimited Lists

- Pipe-delimited fields are split on `|`.
- Each item is stripped and lowercased.
- Blank list fields normalize to an empty tuple.
- Empty parts are ignored.

## Description Text

- Human-facing text is whitespace-normalized: repeated whitespace becomes a single space.
- `normalized_description` is a helper form for matching and grouping: lowercase, non-alphanumeric characters replaced with spaces, then trimmed.
- Raw description text remains available in `raw_source` and `description`.

## Financial Event Classification

- `FinancialEvent` is the shared normalized structure for rows in `financial_events.csv`.
- Investment event types (`investment_purchase`, `investment_sale`, `investment_valuation`) or `non_cash` direction produce an `Investment` instance.
- Income-like event types (`income`, `refund`) or `credit` direction produce an `IncomeEvent` instance, unless already classified as investment.
- Expense-like event types (`expense`, `debt_payment`, `subscription`) or `debit` direction produce an `ExpenseEvent` instance.
- Other cash-like records may become `Transaction`.
- Unrecognized records remain generic `FinancialEvent`.
- Missing event amounts add a `missing_or_uncertain` issue so later evidence resolution can use `images.csv` and image files.

## Duplicates

- The loader counts duplicate full rows for diagnostics.
- The loader validates duplicate primary keys and raises a `DataValidationError` when duplicates exist.
- Normalization does not deduplicate records or choose winners between conflicting records.
