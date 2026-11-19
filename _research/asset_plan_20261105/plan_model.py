"""Three-year financial goal arithmetic, not a return forecast.

All model returns are annual effective RMB total returns after fees, taxes and
currency movements. Contributions arrive at each month end. Emergency cash
remains part of total financial assets, so funding it is not an expense.
"""
import json
from pathlib import Path

FACTS = {
    "as_of": "2026-11-05",
    "target_month": "2029-11",
    "goal_rmb": 1_000_000,
    "usd_product_snapshot_value": 16_545.28,
    "annual_net_income_rmb_latest_answer": 200_000,
    "monthly_living_expense_rmb": 2_000,
    "debt_rmb": 0,
    "marriage_outflow_in_current_scope_rmb": 0,
    "other_assets_in_latest_answer_rmb": 0,
    "provident_fund_available_cash_assumed_rmb": 0,
}
ASSUMPTIONS = {
    "rmb_per_usd_for_planning_only": 6.65,
    "months": 36,
    "annual_extra_expense_reserve_rmb_for_execution": 8_000,
    "emergency_cash_target_rmb_provisional": 50_000,
    "allocation_after_emergency_cash": {"hkd_us_equities": 0.20, "overseas_short_high_quality_bonds": 0.20, "rmb_cash_and_deposits": 0.60},
    "long_term_only_allocation_example": {"hkd_us_equities": 0.50, "overseas_high_quality_bonds": 0.30, "cash": 0.20},
    "note_prior_rmb_cash": "Earlier record mentioned RMB5,000; not added separately after latest 'no other assets' answer.",
}


def annuity_factor(rate, months):
    if rate == 0:
        return months
    monthly = (1 + rate) ** (1 / 12) - 1
    return ((1 + monthly) ** months - 1) / monthly


def future_value(initial, contribution, rate, months):
    return initial * (1 + rate) ** (months / 12) + contribution * annuity_factor(rate, months)


def calculate():
    f, a = FACTS, ASSUMPTIONS
    initial = f["usd_product_snapshot_value"] * a["rmb_per_usd_for_planning_only"]
    annual_save = f["annual_net_income_rmb_latest_answer"] - f["monthly_living_expense_rmb"] * 12
    monthly = annual_save / 12
    execution_monthly = (annual_save - a["annual_extra_expense_reserve_rmb_for_execution"]) / 12
    rows = []
    for rate in [0, 0.03, 0.05, 0.08]:
        needed_monthly = (f["goal_rmb"] - initial * (1 + rate) ** 3) / annuity_factor(rate, 36)
        required_initial = (f["goal_rmb"] - monthly * annuity_factor(rate, 36)) / (1 + rate) ** 3
        needed_after_first_year = (f["goal_rmb"] - future_value(initial, monthly, rate, 12) * (1 + rate)**2) / annuity_factor(rate, 24)
        months_to_goal = next((n for n in range(1, 241) if future_value(initial, monthly, rate, n) >= f["goal_rmb"]), None)
        rows.append({"annual_effective_rmb_net_return_scenario": rate,
                     "year_end_assets_rmb": [future_value(initial, monthly, rate, n) for n in [12,24,36]],
                     "execution_budget_three_year_assets_rmb": future_value(initial, execution_monthly, rate, 36),
                     "required_monthly_savings_for_three_year_goal_rmb": needed_monthly,
                     "required_annual_net_income_excluding_extra_expense_reserve_rmb": needed_monthly*12 + f["monthly_living_expense_rmb"]*12,
                     "required_starting_assets_rmb_at_current_income": required_initial,
                     "additional_starting_assets_rmb": required_initial - initial,
                     "needed_monthly_savings_in_years_2_and_3_if_year_1_unchanged_rmb": needed_after_first_year,
                     "needed_annual_net_income_in_years_2_and_3_rmb": needed_after_first_year*12 + 24_000,
                     "first_whole_month_goal_reached_under_smooth_return_assumption": months_to_goal})
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if future_value(initial, monthly, mid, 36) < f["goal_rmb"]:
            lo = mid
        else:
            hi = mid
    return {"starting_assets_rmb_planning_value": initial,
            "annual_savings_before_other_expenses_rmb": annual_save,
            "monthly_savings_before_other_expenses_rmb": monthly,
            "execution_monthly_savings_rmb": execution_monthly,
            "required_annual_return_if_cashflow_unchanged": (lo+hi)/2,
            "scenarios": rows,
            "hard_goal_zero_return_25000_monthly_saving_checkpoints_rmb": [future_value(initial,25_000,0,n) for n in [12,24,36]],
            "annual_net_income_needed_for_25000_monthly_saving_with_extra_expenses_rmb": 25_000*12+24_000+8_000,
            "allocation_stress_before_fx": 0.6+0.2*0.95+0.2*0.5-1,
            "allocation_stress_with_foreign_assets_fx_down_10pct": 0.6+(0.2*0.95+0.2*0.5)*0.9-1,
            "equity_wipeout_direct_impact_at_5pct_single_stock_weight": -0.05,
            "limits": ["No promise of target achievement or maximum drawdown.",
                       "RMB/USD6.65 is a planning assumption, not a current executable quote.",
                       "Initial USD product is cash management, not a verified bond fund.",
                       "Returns include all holdings including reserves; do not double count dividends.",
                       "No freely withdrawable provident fund balance was supplied."]}


if __name__ == "__main__":
    result = {"facts": FACTS, "assumptions": ASSUMPTIONS, "results": calculate()}
    target = Path(__file__).with_name("plan_model_output.json")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["results"], ensure_ascii=True, indent=2))
