from rollup import RollupSpec


def compute_atomic_arb_cost(
    failure_outcome_A: int,
    failure_outcome_B: int,
    rollup_A: RollupSpec,
    rollup_B: RollupSpec,
    gas_price_A: float,
    gas_price_B: float,
) -> float:
    gas_cost_A_success = gas_price_A * rollup_A.get_gas_units_swap()
    gas_cost_B_success = gas_price_B * rollup_B.get_gas_units_swap()
    gas_cost_A_fail = gas_price_A * rollup_A.get_gas_units_fail()
    gas_cost_B_fail = gas_price_B * rollup_B.get_gas_units_fail()
    if failure_outcome_A == 0 and failure_outcome_B == 0:
        arb_cost = gas_cost_A_success + gas_cost_B_success
    else:
        arb_cost = gas_cost_A_fail + gas_cost_B_fail
    return arb_cost


def compute_non_atomic_arb_cost(
    failure_outcome_A: int,
    failure_outcome_B: int,
    rollup_A: RollupSpec,
    rollup_B: RollupSpec,
    gas_price_A: float,
    gas_price_B: float,
) -> float:
    gas_cost_A_success = gas_price_A * rollup_A.get_gas_units_swap()
    gas_cost_B_success = gas_price_B * rollup_B.get_gas_units_swap()
    gas_cost_A_fail = gas_price_A * rollup_A.get_gas_units_fail()
    gas_cost_B_fail = gas_price_B * rollup_B.get_gas_units_fail()
    arb_cost = (
        gas_cost_A_success * (1 - failure_outcome_A)
        + gas_cost_A_fail * failure_outcome_A
        + gas_cost_B_success * (1 - failure_outcome_B)
        + gas_cost_B_fail * failure_outcome_B
    )
    return arb_cost
