from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
import csv
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "code" / "main.py"
SPEC = importlib.util.spec_from_file_location("buy_or_wait_main", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
main = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = main
SPEC.loader.exec_module(main)


def loaded_row(raw: dict[str, str]) -> main.LoadedRow:
    return main.LoadedRow(row_number=2, raw=raw, parsed={})


def account(
    user_id: str = "user_01",
    currency: str = "USD",
    balance: str = "1000",
    minimum: str = "100",
    payment_methods: tuple[str, ...] = ("full_payment",),
    max_installment_months: int | None = None,
) -> main.Account:
    return main.Account(
        raw_source={},
        issues=(),
        user_id=user_id,
        home_currency=currency,
        current_available_balance=Decimal(balance),
        minimum_balance_to_keep=Decimal(minimum),
        financial_priorities=(),
        protected_categories=(),
        reducible_categories=(),
        stoppable_categories=(),
        payment_methods=payment_methods,
        max_installment_months=max_installment_months,
    )


def request(request_id: str = "request_01", user_id: str = "user_01") -> main.UserRequest:
    return main.UserRequest(
        raw_source={},
        issues=(),
        request_id=request_id,
        user_id=user_id,
        request_date=date(2026, 1, 10),
        request_type="purchase",
        requested_amount=Decimal("200"),
        desired_completion_date=date(2026, 2, 1),
        allows_partial_payment=True,
        request_text="Can I buy it?",
    )


def event(
    event_id: str,
    *,
    amount: str | None,
    currency: str = "USD",
    direction: str = "debit",
    status: str = "settled",
    event_type: str = "expense",
    event_date: date = date(2026, 1, 10),
    settlement_date: date | None = date(2026, 1, 10),
    category: str = "groceries",
    user_id: str = "user_01",
) -> main.FinancialEvent:
    amount_value = Decimal(amount) if amount is not None else None
    cls: type[main.FinancialEvent]
    kind: main.NormalizedEventKind
    if event_type.startswith("investment") or direction == "non_cash":
        cls = main.Investment
        kind = "investment"
    elif direction == "credit":
        cls = main.IncomeEvent
        kind = "income"
    else:
        cls = main.ExpenseEvent
        kind = "expense"
    return cls(
        raw_source={"amount": "" if amount is None else amount},
        issues=(),
        event_id=event_id,
        user_id=user_id,
        event_type=event_type,
        description=f"{category} event",
        normalized_description=f"{category} event",
        category=category,
        direction=direction,
        amount=amount_value,
        currency=currency,
        event_date=event_date,
        settlement_date=settlement_date,
        status=status,
        linked_event_id=None,
        flexibility="fixed",
        minimum_allowed_amount=None,
        kind=kind,
    )


def empty_state(
    *,
    balance: str = "1000",
    currency: str = "USD",
    account_balances: dict[str, Decimal] | None = None,
    payment_methods: tuple[str, ...] = ("full_payment",),
    max_installment_months: int | None = None,
) -> main.FinancialState:
    return main.FinancialState(
        request_id="request_01",
        user_id="user_01",
        request_date=date(2026, 1, 10),
        home_currency=currency,
        current_available_cash=Decimal(balance),
        account_balances=account_balances or {"user_01": Decimal(balance)},
        minimum_balance_to_keep=Decimal("100"),
        payment_methods=payment_methods,
        max_installment_months=max_installment_months,
        pending_credits=[],
        pending_debits=[],
        confirmed_income=[],
        confirmed_expenses=[],
        recurring_income=[],
        recurring_expenses=[],
        upcoming_obligations=[],
        investments=[],
        recent_spending_history=[],
        uncertainties=[],
        audit_trail=[],
    )


def daily_forecast(
    day: date,
    opening: str,
    income: str = "0",
    expenses: str = "0",
) -> main.DailyForecast:
    opening_balance = Decimal(opening)
    expected_income = Decimal(income)
    expected_expenses = Decimal(expenses)
    net_change = expected_income - expected_expenses
    return main.DailyForecast(
        date=day,
        opening_balance=opening_balance,
        expected_income=expected_income,
        expected_expenses=expected_expenses,
        net_change=net_change,
        closing_balance=opening_balance + net_change,
        events=[],
    )


def forecast_from_days(days: list[main.DailyForecast]) -> main.CashFlowForecast:
    return main.CashFlowForecast(
        request_id="request_01",
        user_id="user_01",
        home_currency="USD",
        start_date=days[0].date,
        horizon_days=len(days),
        daily=days,
        confirmed_events=[],
        recurring_estimated_events=[],
        uncertain_events=[],
        audit_trail=[],
    )


def safe_payment(
    *,
    safe_now: str = "200",
    earliest: date | None = date(2026, 1, 10),
    minimum_projected: str = "1000",
    price: str = "200",
) -> main.SafePaymentCalculation:
    return main.SafePaymentCalculation(
        request_id="request_01",
        purchase_price=Decimal(price),
        currency="USD",
        current_available_funds=Decimal("1000"),
        required_buffer=Decimal("100"),
        minimum_projected_balance=Decimal(minimum_projected),
        amount_safe_to_pay=Decimal(safe_now),
        earliest_date_for_full_payment=earliest,
        calculation_explanation="test calculation",
    )


def payment_option(
    *,
    option_id: str = "payment_option_01",
    request_id: str = "request_01",
    amount: str = "75",
    count: int = 3,
    first_date: date = date(2026, 1, 10),
    frequency_days: int | None = 30,
    fee: str = "25",
    total: str = "225",
) -> main.PaymentOption:
    return main.PaymentOption(
        raw_source={},
        issues=(),
        payment_option_id=option_id,
        request_id=request_id,
        payment_method="installments",
        payment_amount=Decimal(amount),
        number_of_payments=count,
        first_payment_date=first_date,
        payment_frequency_days=frequency_days,
        financing_fee=Decimal(fee),
        total_payable_amount=Decimal(total),
    )


def candidate_plan(
    *,
    plan_type: main.CandidatePlanType = "full_payment",
    payments: tuple[tuple[date, str, str | None], ...] = ((date(2026, 1, 10), "200", "800"),),
    amount_paid_immediately: str = "200",
    remaining_amount: str = "0",
    installments: tuple[str, ...] = (),
    total: str = "200",
    fee: str = "0",
    source_option_id: str | None = None,
    is_valid: bool = True,
    preserves_buffer: bool = True,
    rejection_reasons: tuple[str, ...] = (),
) -> main.CandidatePlan:
    plan_payments = tuple(
        main.PlanPayment(
            payment_date=payment_date,
            amount=Decimal(amount),
            projected_balance_after_payment=Decimal(balance) if balance is not None else None,
        )
        for payment_date, amount, balance in payments
    )
    return main.CandidatePlan(
        request_id="request_01",
        plan_type=plan_type,
        amount_paid_immediately=Decimal(amount_paid_immediately),
        remaining_amount=Decimal(remaining_amount),
        payment_dates=tuple(payment.payment_date for payment in plan_payments),
        number_of_installments=len(installments),
        installment_amounts=tuple(Decimal(amount) for amount in installments),
        total_amount_paid=Decimal(total),
        fees_or_additional_costs=Decimal(fee),
        projected_balance_after_each_payment=tuple(payment.projected_balance_after_payment for payment in plan_payments),
        preserves_safety_buffer=preserves_buffer,
        follows_spending_change_restrictions=True,
        is_valid=is_valid,
        payment_plan=plan_payments,
        source_payment_option_id=source_option_id,
        rejection_reasons=rejection_reasons,
        explanation="manual candidate",
    )


def verification(plan: main.CandidatePlan, *, valid: bool = True, reason: str | None = None) -> main.CandidatePlanVerification:
    return main.CandidatePlanVerification(
        plan=plan,
        valid=valid,
        invalid_reason=reason,
        verification_details=(
            main.VerificationCheck(
                name="test_verification",
                passed=valid,
                detail=reason or "valid test plan",
            ),
        ),
    )


def write_dataset_csv(dataset_dir: Path, filename: str, rows: list[dict[str, str]]) -> None:
    columns = [column.name for column in main.DATASET_SPECS[filename].columns]
    with (dataset_dir / filename).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def create_minimal_dataset(dataset_dir: Path) -> None:
    (dataset_dir / "media" / "images").mkdir(parents=True)
    write_dataset_csv(
        dataset_dir,
        "financial_profiles.csv",
        [
            {
                "user_id": "user_01",
                "home_currency": "USD",
                "current_available_balance": "1000",
                "minimum_balance_to_keep": "100",
                "financial_priorities": "keep_emergency_buffer",
                "expense_categories_to_protect": "rent|groceries",
                "expense_categories_user_is_willing_to_reduce": "",
                "expense_categories_user_is_willing_to_stop": "",
                "payment_methods_user_will_consider": "full_payment|partial_payment|installments",
                "max_installment_months": "3",
            }
        ],
    )
    write_dataset_csv(
        dataset_dir,
        "requests.csv",
        [
            {
                "request_id": "request_01",
                "user_id": "user_01",
                "request_date": "2026-01-10",
                "request_type": "purchase",
                "requested_amount": "200",
                "desired_completion_date": "2026-02-01",
                "allows_partial_payment": "true",
                "request_text": "Can I buy this test item?",
            }
        ],
    )
    for filename in (
        "financial_events.csv",
        "exchange_rates.csv",
        "sample_requests.csv",
        "request_payment_options.csv",
        "messages.csv",
        "images.csv",
        "output.csv",
    ):
        write_dataset_csv(dataset_dir, filename, [])


class NormalizationTests(unittest.TestCase):
    def test_parse_date_accepts_required_format_and_rejects_other_formats(self) -> None:
        self.assertEqual(main.parse_date("2026-09-13"), date(2026, 9, 13))
        with self.assertRaises(ValueError):
            main.parse_date("2026/09/13")

    def test_currency_conversion_missing_rate_records_uncertainty(self) -> None:
        uncertainties: list[main.FinancialUncertainty] = []
        money = main.convert_money(
            event_id="event_fx",
            amount=Decimal("10"),
            currency="EUR",
            home_currency="USD",
            conversion_date=date(2026, 1, 10),
            rate_lookup={},
            evidence="test",
            uncertainties=uncertainties,
        )

        self.assertIsNone(money.home_amount)
        self.assertEqual(uncertainties[0].reason, "missing_exchange_rate")

    def test_duplicate_row_and_key_counters_are_deterministic(self) -> None:
        rows = [
            loaded_row({"id": "a", "value": "1"}),
            loaded_row({"id": "a", "value": "1"}),
            loaded_row({"id": "b", "value": "2"}),
        ]

        self.assertEqual(main.count_duplicate_rows(row.raw for row in rows), 1)
        self.assertEqual(main.count_duplicate_keys(rows, ("id",)), 1)

    def test_valid_request_record_preserves_raw_and_normalizes_values(self) -> None:
        row = loaded_row(
            {
                "request_id": " Request_01 ",
                "user_id": " USER_01 ",
                "request_date": "2026-09-04",
                "request_type": "Purchase",
                "requested_amount": "1,234.50",
                "desired_completion_date": "2026/10/01",
                "allows_partial_payment": "yes",
                "request_text": "  Can I buy this now?  ",
            }
        )

        request = main.normalize_user_request(row)

        self.assertEqual(request.request_id, "request_01")
        self.assertEqual(request.user_id, "user_01")
        self.assertEqual(request.request_date, date(2026, 9, 4))
        self.assertEqual(request.desired_completion_date, date(2026, 10, 1))
        self.assertEqual(request.requested_amount, Decimal("1234.50"))
        self.assertTrue(request.allows_partial_payment)
        self.assertEqual(request.request_text, "Can I buy this now?")
        self.assertEqual(request.raw_source["request_id"], " Request_01 ")
        self.assertFalse(request.has_uncertain_values)

    def test_blank_values_become_none_or_empty_collections_without_invention(self) -> None:
        row = loaded_row(
            {
                "user_id": "user_01",
                "home_currency": "usd",
                "current_available_balance": "100",
                "minimum_balance_to_keep": "25",
                "financial_priorities": "",
                "expense_categories_to_protect": "",
                "expense_categories_user_is_willing_to_reduce": "",
                "expense_categories_user_is_willing_to_stop": "",
                "payment_methods_user_will_consider": "full_payment",
                "max_installment_months": "",
            }
        )

        account = main.normalize_account(row)

        self.assertEqual(account.home_currency, "USD")
        self.assertEqual(account.financial_priorities, ())
        self.assertEqual(account.protected_categories, ())
        self.assertIsNone(account.max_installment_months)

    def test_invalid_values_are_marked_uncertain(self) -> None:
        row = loaded_row(
            {
                "rate_date": "2026-99-99",
                "from_currency": "US Dollar",
                "to_currency": "",
                "rate": "not-a-number",
            }
        )

        rate = main.normalize_exchange_rate(row)
        codes = {issue.code for issue in rate.issues}

        self.assertIsNone(rate.rate_date)
        self.assertIsNone(rate.from_currency)
        self.assertIsNone(rate.to_currency)
        self.assertIsNone(rate.rate)
        self.assertTrue({"invalid_date", "invalid_currency", "blank", "invalid_decimal"}.issubset(codes))

    def test_duplicate_records_are_reported_by_loader(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "mini.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["id", "amount"])
                writer.writerow(["a", "1"])
                writer.writerow(["a", "1"])

            spec = main.DatasetSpec(
                "mini.csv",
                (main.ColumnSpec("id", "string"), main.ColumnSpec("amount", "decimal")),
                primary_key=("id",),
            )

            with self.assertRaises(main.DataValidationError) as context:
                main.load_dataset(spec, Path(temp_dir))

        self.assertIn("duplicate primary-key", str(context.exception))

    def test_different_currencies_are_uppercased(self) -> None:
        issues: list[main.NormalizationIssue] = []

        self.assertEqual(main.normalize_currency("usd", "currency", issues), "USD")
        self.assertEqual(main.normalize_currency(" Eur ", "currency", issues), "EUR")
        self.assertEqual(main.normalize_currency("inr", "currency", issues), "INR")
        self.assertEqual(issues, [])

    def test_different_date_formats_normalize_to_date(self) -> None:
        cases = {
            "2026-09-04": date(2026, 9, 4),
            "2026/09/04": date(2026, 9, 4),
            "04-09-2026": date(2026, 9, 4),
            "04/09/2026": date(2026, 9, 4),
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                issues: list[main.NormalizationIssue] = []
                self.assertEqual(main.normalize_date(raw, "date", issues), expected)
                self.assertEqual(issues, [])

    def test_financial_events_are_specialized_by_type(self) -> None:
        base = {
            "event_id": "event_01",
            "user_id": "user_01",
            "event_type": "investment sale",
            "description": "  Fund sale proceeds  ",
            "category": "investment",
            "direction": "credit",
            "amount": "250.00",
            "currency": "eur",
            "event_date": "2026-09-04",
            "settlement_date": "",
            "status": "completed",
            "linked_event_id": "",
            "flexibility": "fixed",
            "minimum_allowed_amount": "",
        }

        event = main.normalize_financial_event(loaded_row(base))

        self.assertIsInstance(event, main.Investment)
        self.assertEqual(event.event_type, "investment_sale")
        self.assertEqual(event.status, "settled")
        self.assertEqual(event.currency, "EUR")
        self.assertEqual(event.normalized_description, "fund sale proceeds")

    def test_missing_amount_resolution_uses_linked_image_evidence(self) -> None:
        event = main.normalize_financial_event(
            loaded_row(
                {
                    "event_id": "event_253",
                    "user_id": "user_03",
                    "event_type": "income",
                    "description": "August 2019 net salary",
                    "category": "salary",
                    "direction": "credit",
                    "amount": "",
                    "currency": "IDR",
                    "event_date": "2019-08-31",
                    "settlement_date": "2019-08-31",
                    "status": "settled",
                    "linked_event_id": "",
                    "flexibility": "fixed",
                    "minimum_allowed_amount": "",
                }
            )
        )
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[
                loaded_row(
                    {
                        "image_id": "image_01",
                        "user_id": "user_03",
                        "request_id": "request_03",
                        "related_event_id": "event_253",
                    }
                )
            ],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={})
        normalized = main.NormalizedDatasets(
            accounts=[],
            requests=[],
            sample_requests=[],
            financial_events=[event],
            exchange_rates=[],
            payment_options=[],
        )

        report = main.resolve_missing_amounts(datasets, normalized)

        self.assertEqual(report.missing_amount_count, 1)
        self.assertEqual(report.resolved_count, 1)
        evidence = report.evidence[0]
        self.assertEqual(evidence.record_id, "event_253")
        self.assertEqual(evidence.resolved_value, Decimal("4365000"))
        self.assertEqual(evidence.status, "resolved")

    def test_missing_amount_without_image_is_unresolved(self) -> None:
        event = main.normalize_financial_event(
            loaded_row(
                {
                    "event_id": "event_missing",
                    "user_id": "user_01",
                    "event_type": "expense",
                    "description": "Missing amount",
                    "category": "groceries",
                    "direction": "debit",
                    "amount": "",
                    "currency": "INR",
                    "event_date": "2026-09-04",
                    "settlement_date": "2026-09-04",
                    "status": "settled",
                    "linked_event_id": "",
                    "flexibility": "fixed",
                    "minimum_allowed_amount": "",
                }
            )
        )
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={})
        normalized = main.NormalizedDatasets([], [], [], [event], [], [])

        report = main.resolve_missing_amounts(datasets, normalized)

        self.assertEqual(report.unresolved_count, 1)
        self.assertIsNone(report.evidence[0].resolved_value)
        self.assertEqual(report.evidence[0].resolution_method, "no_linked_image")

    def test_cropped_image_evidence_is_ambiguous(self) -> None:
        event = main.normalize_financial_event(
            loaded_row(
                {
                    "event_id": "event_1700",
                    "user_id": "user_19",
                    "event_type": "expense",
                    "description": "Delivered grocery order",
                    "category": "groceries",
                    "direction": "debit",
                    "amount": "",
                    "currency": "INR",
                    "event_date": "2024-09-03",
                    "settlement_date": "2024-09-03",
                    "status": "settled",
                    "linked_event_id": "",
                    "flexibility": "fixed",
                    "minimum_allowed_amount": "",
                }
            )
        )
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[
                loaded_row(
                    {
                        "image_id": "image_04",
                        "user_id": "user_19",
                        "request_id": "request_19",
                        "related_event_id": "event_1700",
                    }
                )
            ],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={})
        normalized = main.NormalizedDatasets([], [], [], [event], [], [])

        report = main.resolve_missing_amounts(datasets, normalized)

        self.assertEqual(report.ambiguous_count, 1)
        self.assertEqual(report.evidence[0].status, "ambiguous")
        self.assertIsNone(report.evidence[0].resolved_value)

    def test_ai_image_interpretation_resolves_missing_amount_when_valid(self) -> None:
        missing_event = event("event_ai", amount=None, currency="USD", status="settled")
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[
                loaded_row(
                    {
                        "image_id": "image_99",
                        "user_id": "user_01",
                        "request_id": "request_01",
                        "related_event_id": "event_ai",
                    }
                )
            ],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={"image_99": Path("image_99.png")})
        normalized = main.NormalizedDatasets([], [], [], [missing_event], [], [])

        def ai_client(ai_input: main.AIAssistanceInput) -> dict[str, object]:
            self.assertEqual(ai_input.task, "interpret_image")
            self.assertEqual(ai_input.record_id, "event_ai")
            self.assertIn("Do not", ai_input.prompt)
            return {
                "status": "resolved",
                "extracted_amount": "123.45",
                "currency": "usd",
                "confidence": "0.91",
                "explanation": "Invoice total is clearly visible.",
                "evidence": ["total due 123.45"],
            }

        report = main.resolve_missing_amounts(datasets, normalized, ai_client=ai_client)

        self.assertEqual(report.resolved_count, 1)
        self.assertEqual(report.evidence[0].resolved_value, Decimal("123.45"))
        self.assertEqual(report.evidence[0].resolution_method, "ai_image_interpretation")
        self.assertEqual(report.ai_usage[0].status, "resolved")
        self.assertTrue(report.ai_usage[0].output_valid)

    def test_ai_image_interpretation_rejects_low_confidence_amount(self) -> None:
        missing_event = event("event_ai_low", amount=None, currency="USD", status="settled")
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[
                loaded_row(
                    {
                        "image_id": "image_98",
                        "user_id": "user_01",
                        "request_id": "request_01",
                        "related_event_id": "event_ai_low",
                    }
                )
            ],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={})
        normalized = main.NormalizedDatasets([], [], [], [missing_event], [], [])

        report = main.resolve_missing_amounts(
            datasets,
            normalized,
            ai_client=lambda _: {
                "status": "resolved",
                "extracted_amount": "99.00",
                "confidence": "0.42",
                "evidence": ["blurred total"],
            },
        )

        self.assertEqual(report.unresolved_count, 1)
        self.assertIsNone(report.evidence[0].resolved_value)
        self.assertEqual(report.ai_usage[0].status, "invalid")
        self.assertIn("confidence below", report.ai_usage[0].notes)

    def test_ai_image_interpretation_preserves_ambiguous_output(self) -> None:
        missing_event = event("event_ai_ambiguous", amount=None, currency="USD", status="settled")
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[
                loaded_row(
                    {
                        "image_id": "image_97",
                        "user_id": "user_01",
                        "request_id": "request_01",
                        "related_event_id": "event_ai_ambiguous",
                    }
                )
            ],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={})
        normalized = main.NormalizedDatasets([], [], [], [missing_event], [], [])

        report = main.resolve_missing_amounts(
            datasets,
            normalized,
            ai_client=lambda _: {
                "status": "ambiguous",
                "confidence": "0.80",
                "explanation": "Two totals are visible and the linked event does not identify which one applies.",
            },
        )

        self.assertEqual(report.ambiguous_count, 1)
        self.assertEqual(report.evidence[0].status, "ambiguous")
        self.assertIsNone(report.evidence[0].resolved_value)
        self.assertTrue(report.ai_usage[0].output_valid)

    def test_ai_image_interpretation_rejects_malformed_output(self) -> None:
        missing_event = event("event_ai_bad", amount=None, currency="USD", status="settled")
        image_table = main.LoadedTable(
            spec=main.DATASET_SPECS["images.csv"],
            path=Path("images.csv"),
            columns=["image_id", "user_id", "request_id", "related_event_id"],
            rows=[
                loaded_row(
                    {
                        "image_id": "image_96",
                        "user_id": "user_01",
                        "request_id": "request_01",
                        "related_event_id": "event_ai_bad",
                    }
                )
            ],
            missing_counts={},
            duplicate_row_count=0,
            duplicate_key_count=0,
        )
        datasets = main.LoadedDatasets(tables={"images.csv": image_table}, image_files={})
        normalized = main.NormalizedDatasets([], [], [], [missing_event], [], [])

        report = main.resolve_missing_amounts(
            datasets,
            normalized,
            ai_client=lambda _: {"status": "resolved", "extracted_amount": "not a number", "confidence": "0.95"},
        )

        self.assertEqual(report.unresolved_count, 1)
        self.assertEqual(report.ai_usage[0].status, "invalid")
        self.assertFalse(report.ai_usage[0].output_valid)

    def test_financial_state_buckets_cash_flows_without_decisions(self) -> None:
        req = request()
        acct = account()
        events = [
            event("income_future", amount="500", direction="credit", event_type="income", status="scheduled", event_date=date(2026, 1, 20), settlement_date=date(2026, 1, 20), category="salary"),
            event("pending_credit", amount="75", direction="credit", event_type="refund", status="pending", event_date=date(2026, 1, 11), settlement_date=date(2026, 1, 11), category="refund"),
            event("pending_debit", amount="80", direction="debit", status="pending", event_date=date(2026, 1, 12), settlement_date=date(2026, 1, 12)),
            event("recent_debit", amount="25", direction="debit", status="settled", event_date=date(2026, 1, 1), settlement_date=date(2026, 1, 1)),
            event("failed_debit", amount="999", direction="debit", status="failed", event_date=date(2026, 1, 9), settlement_date=date(2026, 1, 9)),
            event("investment_value", amount="300", currency="USD", direction="non_cash", event_type="investment_valuation", status="unrealized", event_date=date(2026, 1, 9), settlement_date=None, category="investment"),
        ]

        state = main.reconstruct_financial_state_for_request(
            request=req,
            account=acct,
            events=events,
            rate_lookup={},
            resolution_by_event={},
        )

        self.assertEqual(state.current_available_cash, Decimal("1000"))
        self.assertEqual(len(state.confirmed_income), 1)
        self.assertEqual(len(state.pending_credits), 1)
        self.assertEqual(len(state.pending_debits), 1)
        self.assertEqual(len(state.upcoming_obligations), 1)
        self.assertEqual(len(state.recent_spending_history), 1)
        self.assertEqual(len(state.investments), 1)
        self.assertNotIn("failed_debit", {entry.event_id for entry in state.recent_spending_history})
        self.assertTrue(any("pending credit" in note for note in state.audit_trail))

    def test_transaction_filtering_excludes_failed_cancelled_duplicates_and_unrealized_funds(self) -> None:
        req = request()
        acct = account()
        events = [
            event("settled_debit", amount="20", direction="debit", status="settled"),
            event("failed_debit", amount="30", direction="debit", status="failed"),
            event("cancelled_debit", amount="40", direction="debit", status="cancelled"),
            event("duplicate_debit", amount="20", direction="debit", status="settled"),
            event("duplicate_debit", amount="20", direction="debit", status="settled"),
            event("unrealized_gain", amount="999", direction="non_cash", event_type="investment_valuation", status="unrealized"),
        ]

        state = main.reconstruct_financial_state_for_request(
            request=req,
            account=acct,
            events=events,
            rate_lookup={},
            resolution_by_event={},
        )

        self.assertEqual({entry.event_id for entry in state.confirmed_expenses}, {"settled_debit", "duplicate_debit"})
        self.assertEqual([entry.event_id for entry in state.investments], ["unrealized_gain"])
        self.assertTrue(any("failed_debit: excluded" in note for note in state.audit_trail))
        self.assertTrue(any("cancelled_debit: excluded" in note for note in state.audit_trail))
        self.assertTrue(any("duplicate_debit: skipped duplicate event id" in note for note in state.audit_trail))

    def test_financial_state_uses_exact_dated_exchange_rate(self) -> None:
        req = request()
        acct = account(currency="USD")
        eur_event = event("eur_expense", amount="10", currency="EUR", settlement_date=date(2026, 1, 10))

        state = main.reconstruct_financial_state_for_request(
            request=req,
            account=acct,
            events=[eur_event],
            rate_lookup={(date(2026, 1, 10), "EUR", "USD"): Decimal("1.20")},
            resolution_by_event={},
        )

        self.assertEqual(state.recent_spending_history[0].amount.home_amount, Decimal("12.00"))
        self.assertEqual(state.recent_spending_history[0].amount.exchange_rate, Decimal("1.20"))
        self.assertEqual(state.uncertainties, [])

    def test_financial_state_preserves_missing_amount_uncertainty(self) -> None:
        req = request()
        acct = account(currency="INR")
        missing_event = event("event_1700", amount=None, currency="INR", settlement_date=date(2026, 1, 10))
        ambiguous = main.AmountResolutionEvidence(
            record_id="event_1700",
            original_value="",
            resolved_value=None,
            evidence_source="dataset/media/images/image_04.png",
            resolution_method="manual_image_review:cropped_receipt",
            confidence=Decimal("0.40"),
            status="ambiguous",
            notes="Cropped image; final total not reliable.",
        )

        state = main.reconstruct_financial_state_for_request(
            request=req,
            account=acct,
            events=[missing_event],
            rate_lookup={},
            resolution_by_event={"event_1700": ambiguous},
        )

        self.assertEqual(len(state.uncertainties), 1)
        self.assertEqual(state.uncertainties[0].reason, "ambiguous")
        self.assertIsNone(state.recent_spending_history[0].amount)

    def test_reconstruct_financial_states_returns_one_state_per_request(self) -> None:
        normalized = main.NormalizedDatasets(
            accounts=[account()],
            requests=[request()],
            sample_requests=[],
            financial_events=[event("recent_debit", amount="25")],
            exchange_rates=[],
            payment_options=[],
        )

        states = main.reconstruct_financial_states(normalized)

        self.assertEqual(set(states), {"request_01"})
        self.assertEqual(states["request_01"].account_balances["user_01"], Decimal("1000"))

    def test_forecast_with_no_future_events_keeps_balance_flat(self) -> None:
        forecast = main.generate_cash_flow_forecast(empty_state(), horizon_days=3)

        self.assertEqual(len(forecast.daily), 3)
        self.assertEqual([day.closing_balance for day in forecast.daily], [Decimal("1000")] * 3)
        self.assertEqual(forecast.confirmed_events, [])
        self.assertEqual(forecast.recurring_estimated_events, [])

    def test_forecast_includes_regular_salary_pattern(self) -> None:
        req = request()
        acct = account(balance="1000")
        events = [
            event("salary_1", amount="500", direction="credit", event_type="income", status="settled", event_date=date(2025, 11, 11), settlement_date=date(2025, 11, 11), category="salary"),
            event("salary_2", amount="500", direction="credit", event_type="income", status="settled", event_date=date(2025, 12, 11), settlement_date=date(2025, 12, 11), category="salary"),
        ]
        state = main.reconstruct_financial_state_for_request(
            request=req,
            account=acct,
            events=events,
            rate_lookup={},
            resolution_by_event={},
        )

        forecast = main.generate_cash_flow_forecast(state, horizon_days=31)

        self.assertEqual(len(state.recurring_income), 1)
        self.assertEqual(forecast.daily[0].expected_income, Decimal("500"))
        self.assertEqual(forecast.daily[0].closing_balance, Decimal("1500"))
        self.assertEqual(forecast.recurring_estimated_events[0].source_type, "recurring_estimated")

    def test_forecast_includes_recurring_bill_pattern(self) -> None:
        req = request()
        acct = account(balance="1000")
        events = [
            event("bill_1", amount="100", status="settled", event_date=date(2025, 11, 11), settlement_date=date(2025, 11, 11), category="utilities"),
            event("bill_2", amount="100", status="settled", event_date=date(2025, 12, 11), settlement_date=date(2025, 12, 11), category="utilities"),
        ]
        state = main.reconstruct_financial_state_for_request(
            request=req,
            account=acct,
            events=events,
            rate_lookup={},
            resolution_by_event={},
        )

        forecast = main.generate_cash_flow_forecast(state, horizon_days=31)

        self.assertEqual(len(state.recurring_expenses), 1)
        self.assertEqual(forecast.daily[0].expected_expenses, Decimal("100"))
        self.assertEqual(forecast.daily[0].closing_balance, Decimal("900"))

    def test_forecast_applies_large_upcoming_expense(self) -> None:
        state = main.reconstruct_financial_state_for_request(
            request=request(),
            account=account(balance="1000"),
            events=[
                event("large_rent", amount="700", status="scheduled", event_date=date(2026, 1, 20), settlement_date=date(2026, 1, 20), category="rent")
            ],
            rate_lookup={},
            resolution_by_event={},
        )

        forecast = main.generate_cash_flow_forecast(state, horizon_days=11)

        self.assertEqual(forecast.daily[-1].date, date(2026, 1, 20))
        self.assertEqual(forecast.daily[-1].expected_expenses, Decimal("700"))
        self.assertEqual(forecast.daily[-1].closing_balance, Decimal("300"))

    def test_forecast_supports_multiple_account_balance_audit_shape(self) -> None:
        state = empty_state(
            balance="1000",
            account_balances={"checking": Decimal("600"), "savings": Decimal("400")},
        )

        forecast = main.generate_cash_flow_forecast(state, horizon_days=1)

        self.assertEqual(state.account_balances["checking"], Decimal("600"))
        self.assertEqual(state.account_balances["savings"], Decimal("400"))
        self.assertEqual(forecast.daily[0].opening_balance, Decimal("1000"))

    def test_forecast_uses_converted_currency_amounts(self) -> None:
        state = main.reconstruct_financial_state_for_request(
            request=request(),
            account=account(balance="1000", currency="USD"),
            events=[
                event("eur_bill", amount="10", currency="EUR", status="scheduled", event_date=date(2026, 1, 10), settlement_date=date(2026, 1, 10), category="utilities")
            ],
            rate_lookup={(date(2026, 1, 10), "EUR", "USD"): Decimal("1.20")},
            resolution_by_event={},
        )

        forecast = main.generate_cash_flow_forecast(state, horizon_days=1)

        self.assertEqual(forecast.daily[0].expected_expenses, Decimal("12.00"))
        self.assertEqual(forecast.daily[0].closing_balance, Decimal("988.00"))

    def test_forecast_tracks_pending_credit_as_uncertain_without_balance_effect(self) -> None:
        state = main.reconstruct_financial_state_for_request(
            request=request(),
            account=account(balance="1000"),
            events=[
                event("pending_refund", amount="250", direction="credit", event_type="refund", status="pending", event_date=date(2026, 1, 10), settlement_date=date(2026, 1, 10), category="refund")
            ],
            rate_lookup={},
            resolution_by_event={},
        )

        forecast = main.generate_cash_flow_forecast(state, horizon_days=1)

        self.assertEqual(forecast.daily[0].expected_income, Decimal("0"))
        self.assertEqual(forecast.daily[0].closing_balance, Decimal("1000"))
        self.assertEqual(len(forecast.uncertain_events), 1)
        self.assertFalse(forecast.uncertain_events[0].affects_balance)

    def test_safe_payment_caps_at_purchase_price_when_full_amount_is_safe(self) -> None:
        req = request()
        state = empty_state(balance="1000")
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "950"),
            ]
        )

        calculation = main.calculate_safe_payment(req, state, forecast)

        self.assertEqual(calculation.amount_safe_to_pay, Decimal("200"))
        self.assertEqual(calculation.earliest_date_for_full_payment, date(2026, 1, 10))
        self.assertEqual(calculation.minimum_projected_balance, Decimal("950"))

    def test_safe_payment_uses_future_minimum_not_current_balance_only(self) -> None:
        req = request()
        state = empty_state(balance="1000")
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "1000", expenses="850"),
            ]
        )

        calculation = main.calculate_safe_payment(req, state, forecast)

        self.assertEqual(calculation.minimum_projected_balance, Decimal("150"))
        self.assertEqual(calculation.amount_safe_to_pay, Decimal("50"))
        self.assertIsNone(calculation.earliest_date_for_full_payment)

    def test_safe_payment_finds_earliest_later_full_payment_date(self) -> None:
        req = request()
        state = empty_state(balance="1000")
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000", expenses="850"),
                daily_forecast(date(2026, 1, 11), "150", income="300"),
                daily_forecast(date(2026, 1, 12), "450"),
            ]
        )

        calculation = main.calculate_safe_payment(req, state, forecast)

        self.assertEqual(calculation.amount_safe_to_pay, Decimal("50"))
        self.assertEqual(calculation.earliest_date_for_full_payment, date(2026, 1, 12))

    def test_safe_payment_zero_when_forecast_already_below_buffer(self) -> None:
        req = request()
        state = empty_state(balance="1000")
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "90"),
            ]
        )

        calculation = main.calculate_safe_payment(req, state, forecast)

        self.assertEqual(calculation.amount_safe_to_pay, Decimal("0"))
        self.assertIsNone(calculation.earliest_date_for_full_payment)

    def test_safe_payment_handles_exact_buffer_boundary(self) -> None:
        req = request()
        state = empty_state(balance="1000")
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "300"),
                daily_forecast(date(2026, 1, 11), "300"),
            ]
        )

        calculation = main.calculate_safe_payment(req, state, forecast)

        self.assertEqual(calculation.amount_safe_to_pay, Decimal("200"))
        self.assertEqual(calculation.earliest_date_for_full_payment, date(2026, 1, 10))

    def test_candidate_generation_includes_valid_full_payment(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("full_payment",))
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])

        candidates = main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(),
            payment_options=[],
        )

        full = [candidate for candidate in candidates if candidate.plan_type == "full_payment"][0]
        self.assertTrue(full.is_valid)
        self.assertEqual(full.amount_paid_immediately, Decimal("200"))
        self.assertEqual(full.remaining_amount, Decimal("0"))
        self.assertEqual(full.projected_balance_after_each_payment, (Decimal("800"),))

    def test_candidate_generation_includes_valid_partial_payment(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("partial_payment",))
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "1000", income="200"),
                daily_forecast(date(2026, 1, 12), "1200"),
            ]
        )

        candidates = main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="100", earliest=date(2026, 1, 12)),
            payment_options=[],
        )

        partial = [candidate for candidate in candidates if candidate.plan_type == "partial_payment"][0]
        self.assertTrue(partial.is_valid)
        self.assertEqual(partial.amount_paid_immediately, Decimal("100"))
        self.assertEqual(partial.remaining_amount, Decimal("100"))
        self.assertEqual(partial.payment_dates, (date(2026, 1, 10), date(2026, 1, 12)))
        self.assertEqual(partial.total_amount_paid, Decimal("200"))

    def test_candidate_generation_includes_valid_multiple_installments(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("installments",), max_installment_months=3)
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "925"),
                daily_forecast(date(2026, 1, 12), "925"),
            ]
        )
        option = payment_option(amount="75", count=3, first_date=date(2026, 1, 10), frequency_days=1, fee="25", total="225")

        candidates = main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="0", earliest=None),
            payment_options=[option],
        )

        installment = [candidate for candidate in candidates if candidate.plan_type == "installments"][0]
        self.assertTrue(installment.is_valid)
        self.assertEqual(installment.number_of_installments, 3)
        self.assertEqual(installment.installment_amounts, (Decimal("75"), Decimal("75"), Decimal("75")))
        self.assertEqual(installment.fees_or_additional_costs, Decimal("25"))

    def test_candidate_generation_falls_back_when_funds_are_insufficient(self) -> None:
        req = request()
        state = empty_state(balance="100", payment_methods=("full_payment",))
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "100")])
        candidates = main.generate_candidate_plans(
            [req],
            {"request_01": state},
            {"request_01": forecast},
            {"request_01": safe_payment(safe_now="0", earliest=None, minimum_projected="100")},
            [],
        )

        self.assertEqual(len(candidates["request_01"]), 1)
        self.assertEqual(candidates["request_01"][0].plan_type, "not_recommended")

    def test_candidate_generation_rejects_unsafe_future_cash_flow(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("full_payment",))
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "1000", expenses="850"),
            ]
        )

        candidates = main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="50", earliest=None, minimum_projected="150"),
            payment_options=[],
        )

        full = [candidate for candidate in candidates if candidate.plan_type == "full_payment"][0]
        self.assertFalse(full.is_valid)
        self.assertIn("Plan would violate the required safety buffer after one or more payments.", full.rejection_reasons)

    def test_candidate_generation_rejects_invalid_installment_schedule(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("installments",), max_installment_months=3)
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        option = payment_option(amount="75", count=3, first_date=date(2026, 1, 10), frequency_days=None, fee="25", total="225")

        candidates = main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="0", earliest=None),
            payment_options=[option],
        )

        installment = [candidate for candidate in candidates if candidate.plan_type == "installments"][0]
        self.assertFalse(installment.is_valid)
        self.assertIn("Installment payment option is missing payment_frequency_days.", installment.rejection_reasons)

    def test_candidate_verification_accepts_valid_full_payment(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("full_payment",))
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        plan = candidate_plan()

        verification = main.verify_candidate_plan(
            candidate=plan,
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(),
            payment_options=[],
        )

        self.assertTrue(verification.valid)
        self.assertIsNone(verification.invalid_reason)

    def test_candidate_verification_rejects_nonchronological_payments(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("partial_payment",))
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "1000"),
                daily_forecast(date(2026, 1, 12), "1200"),
            ]
        )
        plan = candidate_plan(
            plan_type="partial_payment",
            payments=((date(2026, 1, 12), "100", "1000"), (date(2026, 1, 10), "100", "900")),
            amount_paid_immediately="0",
            remaining_amount="200",
        )

        verification = main.verify_candidate_plan(
            candidate=plan,
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="100", earliest=date(2026, 1, 12)),
            payment_options=[],
        )

        self.assertFalse(verification.valid)
        self.assertIn("payment_dates_chronological", verification.invalid_reason or "")

    def test_candidate_verification_rejects_partial_payment_rule_violation(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("partial_payment",))
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "1100"),
            ]
        )
        plan = candidate_plan(
            plan_type="partial_payment",
            payments=((date(2026, 1, 10), "50", "950"), (date(2026, 1, 11), "150", "900")),
            amount_paid_immediately="50",
            remaining_amount="150",
        )

        verification = main.verify_candidate_plan(
            candidate=plan,
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="100", earliest=date(2026, 1, 11)),
            payment_options=[],
        )

        self.assertFalse(verification.valid)
        self.assertIn("partial_payment_rules", verification.invalid_reason or "")

    def test_candidate_verification_rejects_installment_total_mismatch(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("installments",), max_installment_months=3)
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "925"),
                daily_forecast(date(2026, 1, 12), "925"),
            ]
        )
        option = payment_option(amount="75", count=3, first_date=date(2026, 1, 10), frequency_days=1, fee="25", total="225")
        plan = main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="0", earliest=None),
            payment_options=[option],
        )[2]
        bad_plan = replace(plan, total_amount_paid=Decimal("200"))

        verification = main.verify_candidate_plan(
            candidate=bad_plan,
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="0", earliest=None),
            payment_options=[option],
        )

        self.assertFalse(verification.valid)
        self.assertIn("total_payment_matches_required_amount", verification.invalid_reason or "")

    def test_candidate_verification_rejects_unsafe_buffer(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("full_payment",))
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 11), "1000", expenses="850"),
            ]
        )
        plan = [candidate for candidate in main.generate_candidate_plans_for_request(
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="50", earliest=None, minimum_projected="150"),
            payment_options=[],
        ) if candidate.plan_type == "full_payment"][0]

        verification = main.verify_candidate_plan(
            candidate=plan,
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(safe_now="50", earliest=None, minimum_projected="150"),
            payment_options=[],
        )

        self.assertFalse(verification.valid)
        self.assertIn("required_buffer_preserved", verification.invalid_reason or "")

    def test_candidate_verification_rejects_uncertain_income_dependency(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("full_payment",))
        uncertain_event = main.ForecastEvent(
            event_id="event_uncertain",
            source_type="uncertain",
            date=date(2026, 1, 10),
            direction="credit",
            category="bonus",
            amount=Decimal("200"),
            affects_balance=True,
            explanation="Uncertain bonus should not be guaranteed.",
        )
        forecast = main.CashFlowForecast(
            request_id="request_01",
            user_id="user_01",
            home_currency="USD",
            start_date=date(2026, 1, 10),
            horizon_days=1,
            daily=[
                main.DailyForecast(
                    date=date(2026, 1, 10),
                    opening_balance=Decimal("1000"),
                    expected_income=Decimal("200"),
                    expected_expenses=Decimal("0"),
                    net_change=Decimal("200"),
                    closing_balance=Decimal("1200"),
                    events=[uncertain_event],
                )
            ],
            confirmed_events=[],
            recurring_estimated_events=[],
            uncertain_events=[uncertain_event],
            audit_trail=[],
        )

        verification = main.verify_candidate_plan(
            candidate=candidate_plan(),
            request=req,
            state=state,
            forecast=forecast,
            safe_payment=safe_payment(),
            payment_options=[],
        )

        self.assertFalse(verification.valid)
        self.assertIn("uncertain_income_not_guaranteed", verification.invalid_reason or "")

    def test_verified_candidate_plans_for_ranking_excludes_invalid_plans(self) -> None:
        req = request()
        state = empty_state(balance="1000", payment_methods=("full_payment",))
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        valid_plan = candidate_plan()
        invalid_plan = candidate_plan(payments=((date(2026, 1, 10), "250", "750"),), total="250")

        verified = main.verified_candidate_plans_for_ranking(
            [req],
            {"request_01": state},
            {"request_01": forecast},
            {"request_01": safe_payment()},
            [],
            {"request_01": [valid_plan, invalid_plan]},
        )

        self.assertEqual(verified["request_01"], [valid_plan])

    def test_plan_ranking_equal_cost_prefers_fewer_payments(self) -> None:
        req = request()
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 20), "1000"),
            ]
        )
        full = candidate_plan(plan_type="full_payment")
        partial = candidate_plan(
            plan_type="partial_payment",
            payments=((date(2026, 1, 10), "100", "900"), (date(2026, 1, 20), "100", "800")),
            amount_paid_immediately="100",
            remaining_amount="100",
        )

        result = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(partial), verification(full)],
            forecast=forecast,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.selected_plan.plan_type, "full_payment")
        self.assertIn("number of payments", result.reason_selected)

    def test_plan_ranking_prefers_lower_cost_over_faster_more_expensive_plan(self) -> None:
        req = request()
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 20), "1000"),
            ]
        )
        faster_expensive = candidate_plan(
            plan_type="installments",
            payments=((date(2026, 1, 10), "220", "780"),),
            installments=("220",),
            total="220",
            fee="20",
            source_option_id="payment_option_01",
        )
        cheaper_later = candidate_plan(
            plan_type="wait",
            payments=((date(2026, 1, 20), "200", "800"),),
            amount_paid_immediately="0",
            total="200",
        )

        result = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(faster_expensive), verification(cheaper_later)],
            forecast=forecast,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.selected_plan.plan_type, "wait")
        self.assertIn("total cost", result.reason_selected)

    def test_plan_ranking_prefers_fewer_installments_when_prior_rules_tie(self) -> None:
        req = request()
        forecast = forecast_from_days(
            [
                daily_forecast(date(2026, 1, 10), "1000"),
                daily_forecast(date(2026, 1, 20), "900"),
                daily_forecast(date(2026, 1, 30), "800"),
            ]
        )
        two_payments = candidate_plan(
            plan_type="installments",
            payments=((date(2026, 1, 10), "100", "900"), (date(2026, 1, 20), "100", "800")),
            installments=("100", "100"),
            total="200",
            source_option_id="payment_option_02",
        )
        three_payments = candidate_plan(
            plan_type="installments",
            payments=((date(2026, 1, 10), "80", "920"), (date(2026, 1, 20), "60", "860"), (date(2026, 1, 30), "60", "800")),
            installments=("80", "60", "60"),
            total="200",
            source_option_id="payment_option_01",
        )

        result = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(three_payments), verification(two_payments)],
            forecast=forecast,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.selected_plan.source_payment_option_id, "payment_option_02")
        self.assertIn("number of payments", result.reason_selected)

    def test_plan_ranking_ignores_unsafe_invalid_plan(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        unsafe = candidate_plan(plan_type="full_payment")
        safe_wait = candidate_plan(
            plan_type="wait",
            payments=((date(2026, 1, 10), "200", "800"),),
            total="200",
        )

        result = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(unsafe, valid=False, reason="required_buffer_preserved"), verification(safe_wait)],
            forecast=forecast,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.selected_plan, safe_wait)
        self.assertEqual(len(result.competing_plans_considered), 1)

    def test_plan_ranking_uses_lowest_payment_option_id_for_equally_valid_plans(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        high_id = candidate_plan(
            plan_type="installments",
            payments=((date(2026, 1, 10), "200", "800"),),
            installments=("200",),
            source_option_id="payment_option_09",
        )
        low_id = candidate_plan(
            plan_type="installments",
            payments=((date(2026, 1, 10), "200", "800"),),
            installments=("200",),
            source_option_id="payment_option_01",
        )

        result = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(high_id), verification(low_id)],
            forecast=forecast,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.selected_plan.source_payment_option_id, "payment_option_01")
        self.assertIn("payment option id", result.reason_selected)

    def test_plan_ranking_uses_input_order_when_all_explicit_rules_tie(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 20), "1000")])
        first = candidate_plan(
            plan_type="wait",
            payments=((date(2026, 1, 20), "200", "800"),),
            amount_paid_immediately="0",
            total="200",
        )
        second = candidate_plan(
            plan_type="wait",
            payments=((date(2026, 1, 20), "200", "800"),),
            amount_paid_immediately="0",
            total="200",
        )

        result = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(first), verification(second)],
            forecast=forecast,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.selected_plan, first)
        self.assertIn("input-order tie-break", result.reason_selected)

    def test_final_decision_output_schema_and_payment_plan_format(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        plan = candidate_plan()
        ranking = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(plan)],
            forecast=forecast,
        )
        self.assertIsNotNone(ranking)
        assert ranking is not None

        decision = main.build_final_decision(req, safe_payment(), ranking, forecast)
        main.validate_final_output([decision], [req])
        row = decision.to_output_row()

        self.assertEqual(tuple(row.keys()), main.OUTPUT_COLUMNS)
        self.assertEqual(row["affordability_status"], "affordable_now")
        self.assertEqual(row["recommended_payment_method"], "full_payment")
        self.assertEqual(row["payment_plan"], "2026-01-10:200")
        self.assertEqual(row["earliest_date_for_full_payment"], "2026-01-10")

    def test_output_file_validation_accepts_supported_recommendation(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        plan = candidate_plan()
        ranking = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(plan)],
            forecast=forecast,
        )
        self.assertIsNotNone(ranking)
        assert ranking is not None
        decision = main.build_final_decision(req, safe_payment(), ranking, forecast)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.csv"
            main.write_output_csv([decision], output_path)
            report = main.validate_output_file(
                output_path=output_path,
                requests=[req],
                rankings={"request_01": ranking},
                verifications={"request_01": [verification(plan)]},
                deterministic_reference=[decision],
            )

        self.assertTrue(report.passed)

    def test_output_file_validation_rejects_duplicate_request_ids(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        plan = candidate_plan()
        ranking = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(plan)],
            forecast=forecast,
        )
        self.assertIsNotNone(ranking)
        assert ranking is not None
        decision = main.build_final_decision(req, safe_payment(), ranking, forecast)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.csv"
            main.write_output_csv([decision, decision], output_path)
            report = main.validate_output_file(
                output_path=output_path,
                requests=[req],
                rankings={"request_01": ranking},
                verifications={"request_01": [verification(plan)]},
                raise_on_error=False,
            )

        self.assertFalse(report.passed)
        self.assertTrue(any(check.name == "no_duplicate_request_ids" for check in report.checks if not check.passed))

    def test_output_file_validation_detects_nondeterministic_rows(self) -> None:
        req = request()
        forecast = forecast_from_days([daily_forecast(date(2026, 1, 10), "1000")])
        plan = candidate_plan()
        ranking = main.rank_candidate_plans_for_request(
            request=req,
            verifications=[verification(plan)],
            forecast=forecast,
        )
        self.assertIsNotNone(ranking)
        assert ranking is not None
        decision = main.build_final_decision(req, safe_payment(), ranking, forecast)
        changed = main.FinalDecision(
            request_id=decision.request_id,
            amount_safe_to_pay=decision.amount_safe_to_pay,
            affordability_status=decision.affordability_status,
            recommended_payment_method=decision.recommended_payment_method,
            payment_plan=decision.payment_plan,
            earliest_date_for_full_payment=decision.earliest_date_for_full_payment,
            spending_changes_needed=decision.spending_changes_needed,
            decision_explanation=decision.decision_explanation + " changed",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.csv"
            main.write_output_csv([decision], output_path)
            report = main.validate_output_file(
                output_path=output_path,
                requests=[req],
                rankings={"request_01": ranking},
                verifications={"request_01": [verification(plan)]},
                deterministic_reference=[changed],
                raise_on_error=False,
            )

        self.assertFalse(report.passed)
        self.assertTrue(
            any(check.name == "deterministic_across_repeated_runs" for check in report.checks if not check.passed)
        )


class PipelineIntegrationTests(unittest.TestCase):
    def test_small_dataset_runs_end_to_end_and_writes_valid_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_dir = Path(temp_dir) / "dataset"
            output_path = Path(temp_dir) / "output.csv"
            create_minimal_dataset(dataset_dir)

            result = main.run_pipeline(dataset_dir=dataset_dir, output_path=output_path)
            repeat = main.run_pipeline(dataset_dir=dataset_dir, write_output=False)
            report = main.validate_output_file(
                output_path=output_path,
                requests=result.normalized.requests,
                rankings=result.rankings,
                verifications=result.verifications,
                deterministic_reference=repeat.decisions,
            )

            self.assertEqual(len(result.decisions), 1)
            self.assertTrue(output_path.exists())
            self.assertTrue(report.passed)
            self.assertEqual(result.decisions[0].request_id, "request_01")
            self.assertEqual(result.decisions[0].recommended_payment_method, "full_payment")
            self.assertEqual(result.decisions[0].payment_plan, "2026-01-10:200")


if __name__ == "__main__":
    unittest.main()
