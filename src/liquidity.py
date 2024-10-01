from typing import Tuple


def compute_liquidity_diffs(
    delta_x_A: float,
    delta_y_A: float,
    delta_x_B: float,
    delta_y_B: float,
    i_fail_outcome_A: int,
    i_fail_outcome_B: int,
    atomic: True,
) -> Tuple[float, float]:
    if atomic:
        if (i_fail_outcome_A == 0) and (i_fail_outcome_B == 0):
            liq_diff_x = delta_x_B - delta_x_A
            liq_diff_y = delta_y_A - delta_y_B
        else:
            liq_diff_x = 0.0
            liq_diff_y = 0.0

    else:  # i.e non-atomic
        liq_diff_x = delta_x_B * (1 - i_fail_outcome_B) - delta_x_A * (
            1 - i_fail_outcome_A
        )
        liq_diff_y = delta_y_A * (1 - i_fail_outcome_A) - delta_y_B * (
            1 - i_fail_outcome_B
        )
    return liq_diff_x, liq_diff_y
