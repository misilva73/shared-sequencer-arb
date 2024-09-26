import math
from rollup import RollupSpec
from asset import AssetPriceModel
from typing import Tuple, Dict


def compute_atomic_bundle_profit(
    pure_bundle_A_profit: float,
    pure_bundle_B_profit: float,
    failure_outcome_A: int,
    failure_outcome_B: int,
) -> float:
    if failure_outcome_A == 0 and failure_outcome_B == 0:
        bundle_profit = pure_bundle_A_profit + pure_bundle_B_profit
    else:
        bundle_profit = 0.0
    return bundle_profit


def compute_non_atomic_bundle_profit(
    pure_bundle_A_profit: float, pure_bundle_B_profit: float
) -> float:
    bundle_profit = pure_bundle_A_profit + pure_bundle_B_profit
    return bundle_profit


def compute_pure_bundle_profits(
    rollup_A: RollupSpec,
    rollup_B: RollupSpec,
    failure_outcome_A: int,
    failure_outcome_B: int,
    y_price_model: AssetPriceModel,
) -> Tuple[float, float]:
    # Raise exceptions if some specs are not correct
    check_rollup_specs(rollup_A, rollup_B)
    # Get optimal trade sizes
    trade_sizes_dict = compute_arb_trade_sizes(rollup_A, rollup_B)
    delta_x_A = trade_sizes_dict["delta_x_A"]
    delta_y_A = trade_sizes_dict["delta_y_A"]
    delta_x_B = trade_sizes_dict["delta_x_B"]
    delta_y_B = trade_sizes_dict["delta_y_B"]
    # Generate asset prices and get fee
    y_price = y_price_model.generate_asset_prices(n_samples=1)[0]
    x_price_A = rollup_A.get_arb_pool_price_in_y_units() * y_price
    x_price_B = rollup_B.get_arb_pool_price_in_y_units() * y_price
    fee_stable = y_price_model.get_trading_fee()  # same for both X and Y tokens
    # Compute pure profit for bundle B
    stable_tokens_paid_B = delta_y_B * (1 - fee_stable) * y_price
    stable_tokens_received_B = delta_x_B * (1 - fee_stable) * (x_price_B)
    pure_bundle_profit_B = (stable_tokens_received_B - stable_tokens_paid_B) * (
        1 - failure_outcome_B  # -> pure profit is zero if the bundle execution fails!
    )
    # Compute pure profit for bundle A
    stable_tokens_paid_A = delta_x_A * (1 - fee_stable) * x_price_A
    stable_tokens_received_A = delta_y_A * (1 - fee_stable) * y_price
    pure_bundle_profit_A = (stable_tokens_received_A - stable_tokens_paid_A) * (
        1 - failure_outcome_A  # -> pure profit is zero if the bundle execution fails!
    )
    return pure_bundle_profit_A, pure_bundle_profit_B


def check_rollup_specs(
    rollup_A: RollupSpec,
    rollup_B: RollupSpec,
) -> None:
    price_A = rollup_A.get_arb_pool_price_in_y_units()
    price_B = rollup_B.get_arb_pool_price_in_y_units()
    if price_A <= price_B:
        raise Exception(
            "The pool on rollup A must have a higher price than the pool on rollup B"
        )
    if rollup_A.get_arb_pool_fee() != rollup_B.get_arb_pool_fee():
        raise Exception(
            "The pools on both rollups must have the same fee. The bundle profit formulae makes this assumption!"
        )


def compute_arb_trade_sizes(
    rollup_A: RollupSpec, rollup_B: RollupSpec
) -> Dict[str, float]:
    # Get pool reserves and fee
    x_A, y_A = rollup_A.get_arb_pool_reserves()
    x_B, y_B = rollup_B.get_arb_pool_reserves()
    fee = rollup_A.get_arb_pool_fee()  # should be the same in both rollups!
    # Compute optimal arbitrage trade sizes -> check paper for full derivation!
    delta_y_B = (math.sqrt(x_A * y_A * x_B * y_B) - x_A * y_B) / (
        (1 - fee) * x_A + ((1 - fee) ** 2) * x_B
    )
    delta_x_B = (x_B * (1 - fee) * delta_y_B) / (y_B + (1 - fee) * delta_y_B)
    delta_x_A = delta_x_B
    delta_y_A = (y_A * (1 - fee) * delta_x_A) / (x_A + (1 - fee) * delta_x_A)
    # Store trade sizes in dict
    trade_sizes_dict = {
        "delta_x_A": delta_x_A,
        "delta_y_A": delta_y_A,
        "delta_x_B": delta_x_B,
        "delta_y_B": delta_y_B,
    }
    return trade_sizes_dict
