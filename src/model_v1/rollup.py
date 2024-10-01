from gas import GasPriceModel
from asset import AssetPriceModel
from scipy.stats import bernoulli
from typing import Tuple


class RollupSpec:
    def __init__(
        self,
        fail_rate: float,
        gas_price_model: GasPriceModel,
        gas_units_swap: float,
        gas_units_fail: float,
        arb_pool_reserve_x: float,
        arb_pool_reserve_y: float,
        arb_pool_fee: float,
    ) -> None:
        self.fail_rate = fail_rate
        self.gas_price_model = gas_price_model
        self.gas_units_swap = gas_units_swap
        self.gas_units_fail = gas_units_fail
        self.arb_pool_reserve_x = arb_pool_reserve_x
        self.arb_pool_reserve_y = arb_pool_reserve_y
        self.arb_pool_fee = arb_pool_fee

    def get_fail_rate(self) -> float:
        return self.fail_rate

    def get_gas_price_model(self) -> GasPriceModel:
        return self.gas_price_model

    def get_asset_price_models(self) -> Tuple[AssetPriceModel, AssetPriceModel]:
        return (self.x_price_model, self.y_price_model)

    def get_gas_units_swap(self) -> float:
        return self.gas_units_swap

    def get_gas_units_fail(self) -> float:
        return self.gas_units_fail

    def get_arb_pool_reserves(self) -> Tuple[float, float]:
        return (self.arb_pool_reserve_x, self.arb_pool_reserve_y)

    def get_arb_pool_fee(self) -> float:
        return self.arb_pool_fee

    def get_arb_pool_price_in_y_units(self) -> float:
        return self.arb_pool_reserve_y / self.arb_pool_reserve_x

    def generate_gas_price(self) -> float:
        return self.gas_price_model.generate_gas_prices(n_samples=1)[0]

    def generate_fail_outcome(self) -> float:
        return bernoulli.rvs(self.fail_rate, size=1)[0]
