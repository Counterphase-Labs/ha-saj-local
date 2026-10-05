from datetime import UTC, datetime

import pytest

from saj_modbus_mock.simulation.ledger import EnergyLedger

START = datetime(2026, 6, 30, 23, 59, 0, tzinfo=UTC)
NEXT_DAY = datetime(2026, 7, 1, 0, 0, 0, tzinfo=UTC)
NEXT_YEAR = datetime(2027, 1, 1, 0, 0, 0, tzinfo=UTC)


def ledger(*, initial=1000.0):
    return EnergyLedger(initial_totals_wh={"pv": initial, "load": 0.0}, moment=START)


def test_energy_integrates_power_over_time_into_every_period():
    ledger_ = ledger()

    ledger_.add(flows_w={"pv": 3600.0, "load": 0.0}, dt_s=1, moment=START)

    for period in ("today", "month", "year"):
        assert ledger_.kwh(flow="pv", period=period) == pytest.approx(0.001)
    assert ledger_.kwh(flow="pv", period="total") == pytest.approx(1.001)


def test_a_new_day_restarts_today_but_not_month_or_total():
    ledger_ = ledger(initial=0.0)
    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=START)

    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=NEXT_DAY)

    assert ledger_.kwh(flow="pv", period="today") == pytest.approx(1.0)
    assert ledger_.kwh(flow="pv", period="month") == pytest.approx(1.0)
    assert ledger_.kwh(flow="pv", period="year") == pytest.approx(2.0)
    assert ledger_.kwh(flow="pv", period="total") == pytest.approx(2.0)


def test_a_new_year_restarts_month_and_year():
    ledger_ = ledger(initial=0.0)
    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=START)

    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=NEXT_YEAR)

    assert ledger_.kwh(flow="pv", period="month") == pytest.approx(1.0)
    assert ledger_.kwh(flow="pv", period="year") == pytest.approx(1.0)
    assert ledger_.kwh(flow="pv", period="total") == pytest.approx(2.0)


def test_totals_never_decrease_for_non_negative_power():
    ledger_ = ledger()
    previous = ledger_.kwh(flow="pv", period="total")

    for power in (0.0, 500.0, 0.0, 1200.0):
        ledger_.add(flows_w={"pv": power}, dt_s=60, moment=START)
        assert ledger_.kwh(flow="pv", period="total") >= previous
        previous = ledger_.kwh(flow="pv", period="total")


def test_aligning_to_a_new_moment_zeroes_the_periods_but_keeps_the_total():
    ledger_ = ledger()
    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=START)

    ledger_.align(moment=NEXT_YEAR)
    ledger_.add(flows_w={"pv": 0.0}, dt_s=1, moment=NEXT_YEAR)

    assert ledger_.kwh(flow="pv", period="today") == 0.0
    assert ledger_.kwh(flow="pv", period="total") == pytest.approx(2.0)


def test_clearing_zeroes_every_counter():
    ledger_ = ledger()
    ledger_.add(flows_w={"pv": 3600.0}, dt_s=1, moment=START)

    ledger_.clear()

    assert ledger_.kwh(flow="pv", period="total") == 0.0
    assert ledger_.kwh(flow="pv", period="today") == 0.0


@pytest.mark.parametrize(
    ("later", "today", "month"),
    [
        (datetime(2026, 7, 1, 12, 0, tzinfo=UTC), 1.0, 1.0),
        (datetime(2026, 6, 16, 12, 0, tzinfo=UTC), 1.0, 2.0),
    ],
)
def test_periods_inside_the_same_year_keep_the_year_running(later, today, month):
    start = datetime(2026, 6, 15, 12, 0, tzinfo=UTC)
    ledger_ = EnergyLedger(initial_totals_wh={"pv": 0.0}, moment=start)
    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=start)

    ledger_.add(flows_w={"pv": 3_600_000.0}, dt_s=1, moment=later)

    assert ledger_.kwh(flow="pv", period="today") == pytest.approx(today)
    assert ledger_.kwh(flow="pv", period="month") == pytest.approx(month)
    assert ledger_.kwh(flow="pv", period="year") == pytest.approx(2.0)
