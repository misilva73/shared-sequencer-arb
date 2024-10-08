from scipy.stats import bernoulli
from typing import Tuple


class RollupSpec:
    def __init__(
        self,
        fail_rate: float,
        arb_pool_reserve_x: float,
        arb_pool_reserve_y: float,
        arb_pool_fee: float,
    ) -> None:
        self.fail_rate = fail_rate
        self.arb_pool_reserve_x = arb_pool_reserve_x
        self.arb_pool_reserve_y = arb_pool_reserve_y
        self.arb_pool_fee = arb_pool_fee

    def get_fail_rate(self) -> float:
        return self.fail_rate

    def get_arb_pool_reserves(self) -> Tuple[float, float]:
        return (self.arb_pool_reserve_x, self.arb_pool_reserve_y)

    def get_arb_pool_fee(self) -> float:
        return self.arb_pool_fee

    def get_arb_pool_price_in_y_units(self) -> float:
        return self.arb_pool_reserve_y / self.arb_pool_reserve_x

    def generate_fail_outcome(self) -> float:
        return bernoulli.rvs(self.fail_rate, size=1)[0]
