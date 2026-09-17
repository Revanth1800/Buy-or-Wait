# AI Assistance Boundary

AI assistance is optional and bounded. It may help interpret language or images, but deterministic Python code remains responsible for every financial calculation and decision.

## Allowed AI Tasks

- Interpret user messages.
- Extract structured purchase details from text.
- Interpret relevant images.
- Resolve ambiguous descriptions.
- Explain evidence in natural language.

## Prohibited AI Tasks

- Final balance calculations.
- Currency conversion arithmetic.
- Forecast arithmetic.
- Safety-buffer calculations.
- Installment arithmetic.
- Candidate validation.
- Final plan ranking.
- Writing arbitrary output values.

## Structured Input

`AIAssistanceInput` includes:

- `task`
- `record_id`
- `source_reference`
- `prompt`
- `structured_context`
- `allowed_output_fields`

The prompt instructs the AI to treat messages and images as evidence only, never as instructions that override challenge rules.

## Structured Output

`AIAssistanceOutput` includes:

- `task`
- `record_id`
- `status`: `resolved`, `unresolved`, `ambiguous`, or `invalid`
- `extracted_amount`
- `currency`
- `normalized_text`
- `explanation`
- `confidence`
- `evidence`

## Validation And Fallback

AI output is accepted only when it matches the expected task and record, has confidence in the `0..1` range, supplies required fields for a resolved value, and meets the minimum confidence threshold.

If AI output is missing, malformed, low confidence, or ambiguous, the affected value remains unresolved or ambiguous. The system never invents a missing amount.

## Usage And Evidence Tracking

Every AI attempt produces an `AIUsageRecord` with:

- task
- record ID
- source reference
- whether an AI client was used
- status
- confidence
- output validity
- notes

When a missing amount is resolved by validated image interpretation, the amount-resolution evidence records `ai_image_interpretation` as the method and carries confidence plus explanatory notes.
