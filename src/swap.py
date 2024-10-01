import math
from rollup import RollupSpec
from typing import Tuple


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
) -> Tuple[float, float, float, float]:
    # Raise exceptions if some specs are not correct
    check_rollup_specs(rollup_A, rollup_B)
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
    return delta_x_A, delta_y_A, delta_x_B, delta_y_B


def compute_prices_after_arb(
    rollup_A: RollupSpec,
    rollup_B: RollupSpec,
    delta_x_A: float,
    delta_y_A: float,
    delta_x_B: float,
    delta_y_B: float,
) -> float:
    # Raise exceptions if some specs are not correct
    check_rollup_specs(rollup_A, rollup_B)
    # Get pool reserves and fee
    x_A, y_A = rollup_A.get_arb_pool_reserves()
    x_B, y_B = rollup_B.get_arb_pool_reserves()
    fee = rollup_A.get_arb_pool_fee()
    # Compute prices after arbitrage
    price_end_B = (y_B + (1 - fee) * delta_y_B) / (x_B - delta_x_B)
    price_end_A = (y_A - delta_y_A) / (x_A + (1 - fee) * delta_x_A)
    return price_end_A, price_end_B


def compute_arb_opportunity_threshold(
    rollup_A: RollupSpec, rollup_B: RollupSpec
) -> float:
    # Raise exceptions if some specs are not correct
    check_rollup_specs(rollup_A, rollup_B)
    # Get pool reserves and fee
    x_A, y_A = rollup_A.get_arb_pool_reserves()
    x_B, y_B = rollup_B.get_arb_pool_reserves()
    fee = rollup_A.get_arb_pool_fee()
    # Compute threshold
    thres_num = x_B * y_A * (1 - fee) * (1 - fee)
    thres_denum = math.sqrt(x_A * y_A * x_B * y_B)
    threshold = thres_num / thres_denum
    return threshold


def contains_arb_opportunity(rollup_A: RollupSpec, rollup_B: RollupSpec) -> bool:
    threshold = compute_arb_opportunity_threshold(rollup_A, rollup_B)
    if threshold > 1:
        return True
    else:
        return False
