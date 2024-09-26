import pandas as pd
import cost
import bundle
from rollup import RollupSpec
from asset import AssetPriceModel
from gas import GasPriceModel


def run_arb_profit_simulation(
    n_iter: int,
    rollup_A: RollupSpec,
    rollup_B: RollupSpec,
    y_price_model: AssetPriceModel,
) -> pd.DataFrame:

    # Compute profit under each regime - atomic vs. non-atomic transactions
    arb_sim_df = pd.DataFrame()
    for i in range(n_iter):
        # Generate failure outcomes for iter
        i_fail_outcome_A = rollup_A.generate_fail_outcome()
        i_fail_outcome_B = rollup_B.generate_fail_outcome()
        # Generate gas prices for iter
        i_gas_price_A = rollup_A.generate_gas_price()
        i_gas_price_B = rollup_B.generate_gas_price()
        # Compute pure bundle profits for iter
        i_pure_bundle_profit_A, i_pure_bundle_profit_B = (
            bundle.compute_pure_bundle_profits(
                rollup_A,
                rollup_B,
                i_fail_outcome_A,
                i_fail_outcome_B,
                y_price_model,
            )
        )
        i_atomic_bundle_profit = bundle.compute_atomic_bundle_profit(
            i_pure_bundle_profit_A,
            i_pure_bundle_profit_B,
            i_fail_outcome_A,
            i_fail_outcome_B,
        )
        i_non_atomic_bundle_profit = bundle.compute_non_atomic_bundle_profit(
            i_pure_bundle_profit_A,
            i_pure_bundle_profit_B,
        )
        # Compute arb cost for iter
        i_atomic_arb_cost = cost.compute_atomic_arb_cost(
            i_fail_outcome_A,
            i_fail_outcome_B,
            rollup_A,
            rollup_B,
            i_gas_price_A,
            i_gas_price_B,
        )
        i_non_atomic_arb_cost = cost.compute_non_atomic_arb_cost(
            i_fail_outcome_A,
            i_fail_outcome_B,
            rollup_A,
            rollup_B,
            i_gas_price_A,
            i_gas_price_B,
        )
        # Compute final profits for iter
        i_atomic_profit = i_atomic_bundle_profit - i_atomic_arb_cost
        i_non_atomic_profit = i_non_atomic_bundle_profit - i_non_atomic_arb_cost
        # store results in DataFramwe
        iter_df = pd.DataFrame(
            {
                "iter": [i],
                "fail_outcome_A": [i_fail_outcome_A],
                "fail_outcome_B": [i_fail_outcome_B],
                "gas_price_A": [i_gas_price_A],
                "gas_price_B": [i_gas_price_B],
                "pure_bundle_profit_A": [i_pure_bundle_profit_A],
                "pure_bundle_profit_B": [i_pure_bundle_profit_B],
                "atomic_bundle_profit": [i_atomic_bundle_profit],
                "non_atomic_bundle_profit": [i_non_atomic_bundle_profit],
                "atomic_arb_cost": [i_atomic_arb_cost],
                "non_atomic_arb_cost": [i_non_atomic_arb_cost],
                "atomic_profit": [i_atomic_profit],
                "non_atomic_profit": [i_non_atomic_profit],
                "shared_sequencing_gain": [i_atomic_profit - i_non_atomic_profit],
            }
        )
        arb_sim_df = pd.concat([arb_sim_df, iter_df], ignore_index=True)
    return arb_sim_df


if __name__ == "__main__":
    # Define rollup settings
    gas_price_model_A = GasPriceModel(
        model_type="gaussian", gas_price_mean=0.01, gas_price_std=0.0001
    )
    rollup_A = RollupSpec(
        fail_rate=0.5,
        gas_price_model=gas_price_model_A,
        gas_units_swap=10.0,
        gas_units_fail=1.0,
        arb_pool_reserve_x=1000.0,
        arb_pool_reserve_y=1050.0,
        arb_pool_fee=0.005,
    )
    gas_price_model_B = GasPriceModel(
        model_type="gaussian", gas_price_mean=0.01, gas_price_std=0.0001
    )
    rollup_B = RollupSpec(
        fail_rate=0.5,
        gas_price_model=gas_price_model_A,
        gas_units_swap=10.0,
        gas_units_fail=1.0,
        arb_pool_reserve_x=1000.0,
        arb_pool_reserve_y=1000.0,
        arb_pool_fee=0.005,
    )
    # Define asset price settings
    y_price_model = AssetPriceModel(
        asset_label="X", fee=0.005, model_type="constant", asset_price_mean=50.0
    )
    # Run simulation
    n_iter = 10
    arb_sim_df = run_arb_profit_simulation(n_iter, rollup_A, rollup_B, y_price_model)
    arb_sim_df.to_csv("./data/test_arb_sim_df.csv", index=False)
