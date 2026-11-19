"""CNOOC dual-counter worksheet. Facts and valuation assumptions are separate.

Run with Python 3; outputs JSON beside this script. Currency conversion inputs
are modeling assumptions, not live executable foreign-exchange quotes.
"""
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
FACTS = {
    "shares": 47_529_953_984,
    "quote_time_beijing": "2026-11-05 10:45 (delayed quote)",
    "hkd_bid": 22.98,
    "hkd_ask": 23.00,
    "cnh_bid": 19.52,
    "cnh_ask": 19.55,
    "hkd_volume_shares": 84_634_975,
    "cnh_volume_shares": 47_000,
    "board_lot_shares_launch_announcement": 1000,
    "profit_2025_rmb": 122_082_000_000,
    "ocf_2025_rmb": 209_042_000_000,
    "cash_capex_2025_rmb": 111_555_000_000,
    "interest_paid_2025_rmb": 3_134_000_000,
    "lease_repayments_2025_rmb": 3_381_000_000,
    "profit_2026_9m_rmb": 119_118_000_000,
    "ocf_2026_9m_rmb": 199_586_000_000,
    "cash_fixed_intangible_long_term_assets_2026_9m_rmb": 81_699_000_000,
    "dividend_2025_hkd": 1.28,
    "dividend_2025_final_hkd": 0.55,
    "dividend_2026_interim_hkd": 0.94,
    "known_usd_product_value": 16_545.28,
}
ASSUMPTIONS = {
    "rmb_per_hkd": 0.85,
    "hkd_per_usd": 7.8,
    "effective_dividend_tax_rate_for_example": 0.20,
    "cash_after_tax_yield_for_example": 0.04,
    "normal_profit_rmb_range": [110_000_000_000, 130_000_000_000],
    "normal_pe_range": [7, 8],
    "normal_payout_ratio_for_example": 0.45,
    "fair_value_hkd_judgment_range": [20, 26],
    "fair_value_midpoint_hkd": 23,
    "initial_single_stock_weight_example": 0.05,
}


def capitalized_cash_value(fcf_rmb, required_yield, rmb_per_hkd):
    return fcf_rmb / required_yield / FACTS["shares"] / rmb_per_hkd


def calculate():
    f, a = FACTS, ASSUMPTIONS
    r = a["rmb_per_hkd"]
    price = f["hkd_ask"]
    market_cap = price * r * f["shares"]
    fcf = f["ocf_2025_rmb"] - f["cash_capex_2025_rmb"]
    adjusted = fcf - f["interest_paid_2025_rmb"] - f["lease_repayments_2025_rmb"]
    trailing_div = f["dividend_2025_final_hkd"] + f["dividend_2026_interim_hkd"]
    net_div = trailing_div * (1 - a["effective_dividend_tax_rate_for_example"])
    cash_rate = a["cash_after_tax_yield_for_example"]
    normal_dividends = [x * a["normal_payout_ratio_for_example"] / f["shares"] / r
                        for x in a["normal_profit_rmb_range"]]
    discounted_years = None
    if net_div > price * cash_rate:
        discounted_years = -math.log(1 - price * cash_rate / net_div) / math.log(1 + cash_rate)
    scenarios = []
    for name, oil_context, lo, hi, hurdle in [
        ("stress", "illustrative Brent USD55-60/bbl; not a fitted forecast", 60e9, 75e9, 0.12),
        ("normal", "illustrative Brent USD65-75/bbl; not a fitted forecast", 85e9, 105e9, 0.10),
        ("high_oil", "illustrative Brent USD80-90/bbl; not a fitted forecast", 120e9, 150e9, 0.10),
    ]:
        scenarios.append({"name": name, "oil_context": oil_context,
                          "annual_cash_proxy_rmb_range": [lo, hi],
                          "required_cash_yield_before_personal_tax": hurdle,
                          "hkd_value_range": [capitalized_cash_value(lo, hurdle, r),
                                              capitalized_cash_value(hi, hurdle, r)]})
    return {
        "market_cap_rmb_if_all_shares_marked_at_hk_price": market_cap,
        "pe_on_2025_profit": market_cap / f["profit_2025_rmb"],
        "simple_fcf_2025_rmb": fcf,
        "cash_proxy_2025_after_interest_and_leases_rmb": adjusted,
        "simple_fcf_2026_9m_rmb": f["ocf_2026_9m_rmb"] - f["cash_fixed_intangible_long_term_assets_2026_9m_rmb"],
        "simple_fcf_2025_yield": fcf / market_cap,
        "adjusted_cash_proxy_2025_yield": adjusted / market_cap,
        "normal_pe_implied_hkd_range": [a["normal_profit_rmb_range"][0] * a["normal_pe_range"][0] / f["shares"] / r,
                                        a["normal_profit_rmb_range"][1] * a["normal_pe_range"][1] / f["shares"] / r],
        "normal_annual_dividend_hkd_range_example": normal_dividends,
        "normal_net_dividend_yield_range_example": [x * (1-a["effective_dividend_tax_rate_for_example"]) / price
                                                    for x in normal_dividends],
        "normal_cash_value_hkd_at_12_percent_hurdle": [capitalized_cash_value(x, 0.12, r) for x in [85e9, 105e9]],
        "counter_break_even_cnh_per_hkd_before_fees": f["cnh_ask"] / price,
        "hkd_quoted_spread_ratio": (f["hkd_ask"] - f["hkd_bid"]) / f["hkd_ask"],
        "cnh_quoted_spread_ratio": (f["cnh_ask"] - f["cnh_bid"]) / f["cnh_ask"],
        "trailing_declared_dividend_hkd": trailing_div,
        "dividend_2025_gross_yield": f["dividend_2025_hkd"] / price,
        "dividend_2025_net_yield_example": f["dividend_2025_hkd"] * 0.8 / price,
        "trailing_dividend_gross_yield": trailing_div / price,
        "trailing_dividend_net_yield_example": net_div / price,
        "static_net_dividend_cost_coverage_years": price / net_div,
        "discounted_dividend_cost_coverage_years_at_cash_hurdle": discounted_years,
        "net_income_spread_over_cash_example": net_div / price - cash_rate,
        "one_lot_usd_at_assumed_fx": price * 1000 / a["hkd_per_usd"],
        "one_lot_as_share_of_known_usd_product_only": price * 1000 / a["hkd_per_usd"] / f["known_usd_product_value"],
        "midpoint_less_20_percent_hkd": a["fair_value_midpoint_hkd"] * 0.8,
        "midpoint_less_30_percent_hkd": a["fair_value_midpoint_hkd"] * 0.7,
        "scenarios": scenarios,
        "price_sensitivity": [{"hkd_price": p, "cnh_equivalent_at_assumed_fx": p * r,
                                "trailing_gross_dividend_yield": trailing_div / p,
                                "net_dividend_yield_example": net_div / p,
                                "static_net_dividend_coverage_years": p / net_div}
                               for p in [16, 18, 18.5, 19, 20, 23, 26]],
        "fx_sensitivity": [{"rmb_per_hkd": x, "hkd_path_cost_cnh_before_fees": price * x,
                             "fair_value_cnh_range": [20*x, 26*x],
                             "initial_research_price_cnh_range": [18*x, 19*x]}
                            for x in [0.80, 0.85, 0.90]],
    }


if __name__ == "__main__":
    output = {"facts": FACTS, "assumptions": ASSUMPTIONS, "results": calculate(),
              "limits": ["Not a reserve-by-reserve DCF or guaranteed return.",
                         "Cash capitalization assumes sustainable reinvestment and reserve replacement; no net cash added.",
                         "Dividend cost coverage excludes terminal stock value, FX movements and reinvestment.",
                         "Account access, nominee withholding, personal tax/credit and broker charges require confirmation."]}
    dest = BASE / "valuation_model_output.json"
    dest.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output["results"], ensure_ascii=False, indent=2))
