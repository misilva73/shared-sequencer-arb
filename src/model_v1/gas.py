import numpy as np
from scipy.stats import norm
from typing import Tuple, List
from numpy.typing import NDArray
from sklearn.neighbors import KernelDensity


class GasPriceModel:
    def __init__(
        self,
        model_type: str = "constant",
        gas_price_mean: float = 0.0,  # used for gaussian model or constant
        gas_price_std: float = 1.0,  # used for gaussian model
        gas_price_histogram: List[Tuple[float, float]] = [
            (1, 1)
        ],  # used for empirical model; shape: (val, count)
    ) -> None:
        if model_type not in ["gaussian", "empirical", "constant"]:
            raise AttributeError(
                'model_type should be "constant", "gaussian" or "empirical"'
            )
        self.model_type = model_type
        self.gas_price_mean = gas_price_mean
        self.gas_price_std = gas_price_std
        self.gas_price_histogram = gas_price_histogram

    def get_model_type(self) -> str:
        return self.model_type

    def generate_gas_prices(self, n_samples: int) -> NDArray:
        if self.model_type == "gaussian":
            gas_prices = norm.rvs(
                loc=self.gas_price_mean, scale=self.gas_price_std, size=n_samples
            )
        elif self.model_type == "constant":
            gas_prices = np.ones(n_samples) * self.gas_price_mean
        elif self.model_type == "empirical":
            vals = np.array([t[0] for t in self.gas_price_histogram]).reshape(-1, 1)
            counts = np.array([t[1] for t in self.gas_price_histogram])
            bandwidth = np.diff(vals).mean()
            kde_model = KernelDensity(kernel="gaussian", bandwidth=bandwidth).fit(
                vals, sample_weight=counts
            )
            gas_prices = kde_model.sample(n_samples).reshape(-1)
        return gas_prices
