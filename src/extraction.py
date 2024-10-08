import warnings
import numpy as np
import pandas as pd
import swap
from rollup import RollupSpec
from liquidity import compute_liquidity_diffs


def compute_expected_profit_diff(
    rollup_A: RollupSpec, rollup_B: RollupSpec, external_price: float
) -> float:
    if not swap.contains_arb_opportunity(rollup_A, rollup_B):
        warnings.warn("Current pool specs do not contain a profitable arbitrage")
    # Compute optimal arbitrage trade sizes
    delta_x_A, delta_y_A, delta_x_B, delta_y_B = swap.compute_arb_trade_sizes(
        rollup_A, rollup_B
    )
    # Compute prices experienced by arbitrageur
    arb_price_A = delta_y_A / delta_x_A
    arb_price_B = delta_y_B / delta_x_B
    # Get failure rates
    fail_rate_A = rollup_A.get_fail_rate()
    fail_rate_B = rollup_B.get_fail_rate()
    # compute expected profit diff -> check paper for full derivation
    profit_diff = delta_x_B * (
        fail_rate_A * (arb_price_B - external_price)
        + fail_rate_B * (external_price - arb_price_A)
        + fail_rate_A * fail_rate_B * (arb_price_A - arb_price_B)
    )
    return profit_diff


def run_arb_profit_simulation(
    n_iter: int, rollup_A: RollupSpec, rollup_B: RollupSpec, external_price: float
) -> pd.DataFrame:
    # Compute profit under each regime - atomic vs. non-atomic transactions
    arb_sim_df = pd.DataFrame()
    for i in range(n_iter):
        if swap.contains_arb_opportunity(rollup_A, rollup_B):
            iter_df = compute_arb_profit_for_iter(i, rollup_A, rollup_B, external_price)
        else:
            iter_df = pd.DataFrame(
                {
                    "iter": [i],
                    "fail_outcome_A": [np.nan],
                    "fail_outcome_B": [np.nan],
                    "contains_arb": [False],
                    "price_diff": [
                        rollup_A.get_arb_pool_price_in_y_units()
                        / rollup_B.get_arb_pool_price_in_y_units()
                    ],
                    "delta_x_A": [np.nan],
                    "delta_y_A": [np.nan],
                    "delta_x_B": [np.nan],
                    "delta_y_B": [np.nan],
                    "liq_diff_x_atomic": [0.0],
                    "liq_diff_y_atomic": [0.0],
                    "total_liq_diff_atomic": [0.0],
                    "liq_diff_x_non_atomic": [0.0],
                    "liq_diff_y_non_atomic": [0.0],
                    "total_liq_diff_non_atomic": [0.0],
                    "shared_sequencing_diff_x": [0.0],
                    "shared_sequencing_diff_y": [0.0],
                    "price_end": [np.nan],
                    "total_shared_sequencing_diff": [0.0],
                }
            )
        arb_sim_df = pd.concat([arb_sim_df, iter_df], ignore_index=True)
    return arb_sim_df


def compute_arb_profit_for_iter(
    iter: int, rollup_A: RollupSpec, rollup_B: RollupSpec, external_price: float
) -> pd.DataFrame:
    # Generate failure outcomes for iter
    i_fail_outcome_A = rollup_A.generate_fail_outcome()
    i_fail_outcome_B = rollup_B.generate_fail_outcome()
    # Compute optimal arbitrage trade sizes
    delta_x_A, delta_y_A, delta_x_B, delta_y_B = swap.compute_arb_trade_sizes(
        rollup_A, rollup_B
    )
    # Compute liquidity chnages after arbitrage
    liq_diff_x_atomic, liq_diff_y_atomic = compute_liquidity_diffs(
        delta_x_A,
        delta_y_A,
        delta_x_B,
        delta_y_B,
        i_fail_outcome_A,
        i_fail_outcome_B,
        atomic=True,
    )
    liq_diff_x_non_atomic, liq_diff_y_non_atomic = compute_liquidity_diffs(
        delta_x_A,
        delta_y_A,
        delta_x_B,
        delta_y_B,
        i_fail_outcome_A,
        i_fail_outcome_B,
        atomic=False,
    )
    # Compute prices after arbitrage -> should be the same
    price_end_A, price_end_B = swap.compute_prices_after_arb(
        rollup_A,
        rollup_B,
        delta_x_A,
        delta_y_A,
        delta_x_B,
        delta_y_B,
    )
    if np.round(price_end_A, 9) != np.round(price_end_B, 9):
        warnings.warn(
            "There is a problem with the code: \n"
            + f"P_end_B={np.round(price_end_B, 9)} != P_end_A={np.round(price_end_A, 9)}"
        )
    # store results in DataFrame
    price_A = rollup_A.get_arb_pool_price_in_y_units()
    price_B = rollup_B.get_arb_pool_price_in_y_units()
    iter_df = pd.DataFrame(
        {
            "iter": [iter],
            "fail_outcome_A": [i_fail_outcome_A],
            "fail_outcome_B": [i_fail_outcome_B],
            "contains_arb": [True],
            "price_diff": [(price_A - price_B) / price_B],
            "delta_x_A": [delta_x_A],
            "delta_y_A": [delta_y_A],
            "delta_x_B": [delta_x_B],
            "delta_y_B": [delta_y_B],
            "liq_diff_x_atomic": [liq_diff_x_atomic],
            "liq_diff_y_atomic": [liq_diff_y_atomic],
            "total_liq_diff_atomic": [
                liq_diff_y_atomic + liq_diff_x_atomic * external_price
            ],
            "liq_diff_x_non_atomic": [liq_diff_x_non_atomic],
            "liq_diff_y_non_atomic": [liq_diff_y_non_atomic],
            "total_liq_diff_non_atomic": [
                liq_diff_y_non_atomic + liq_diff_x_non_atomic * external_price
            ],
            "shared_sequencing_diff_x": [liq_diff_x_atomic - liq_diff_x_non_atomic],
            "shared_sequencing_diff_y": [liq_diff_y_atomic - liq_diff_y_non_atomic],
            "price_end": [price_end_A],
            "total_shared_sequencing_diff": [
                (liq_diff_x_atomic - liq_diff_x_non_atomic) * external_price
                + liq_diff_y_atomic
                - liq_diff_y_non_atomic
            ],
        }
    )
    return iter_df


if __name__ == "__main__":
    # Define rollup settings
    rollup_A = RollupSpec(
        fail_rate=0.5,
        arb_pool_reserve_x=1000.0,
        arb_pool_reserve_y=1050.0,
        arb_pool_fee=0.005,
    )
    rollup_B = RollupSpec(
        fail_rate=0.5,
        arb_pool_reserve_x=1000.0,
        arb_pool_reserve_y=1000.0,
        arb_pool_fee=0.005,
    )
    external_price = 1.0
    # Run simulation
    n_iter = 10
    arb_sim_df = run_arb_profit_simulation(n_iter, rollup_A, rollup_B, external_price)
    arb_sim_df.to_csv("./data/test_arb_sim_df.csv", index=False)
