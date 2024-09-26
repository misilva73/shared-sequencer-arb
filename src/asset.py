import numpy as np
from scipy.stats import norm
from typing import Tuple, List
from numpy.typing import NDArray
from sklearn.neighbors import KernelDensity


class AssetPriceModel:
    def __init__(
        self,
        asset_label: str,
        fee: float,
        model_type: str = "constant",
        asset_price_mean: float = 0.0,  # used for gaussian model or constant
        asset_price_std: float = 1.0,  # used for gaussian model
        asset_price_histogram: List[Tuple[float, float]] = [
            (1, 1)
        ],  # used for empirical model; shape: (val, count)
    ) -> None:
        if model_type not in ["gaussian", "empirical", "constant"]:
            raise AttributeError(
                'model_type should be "constant", "gaussian" or "empirical"'
            )
        self.model_type = model_type
        self.fee = fee
        self.asset_label = asset_label
        self.asset_price_mean = asset_price_mean
        self.asset_price_std = asset_price_std
        self.asset_price_histogram = asset_price_histogram
        if model_type == "empirical":
            vals = np.array([t[0] for t in self.asset_price_histogram]).reshape(-1, 1)
            counts = np.array([t[1] for t in self.asset_price_histogram])
            bandwidth = np.diff(vals).mean()
            self.kde_model = KernelDensity(kernel="gaussian", bandwidth=bandwidth).fit(
                vals, sample_weight=counts
            )

    def get_model_type(self) -> str:
        return self.model_type

    def get_trading_fee(self) -> str:
        return self.fee

    def generate_asset_prices(self, n_samples: int) -> NDArray:
        if self.model_type == "gaussian":
            asset_price = norm.rvs(
                loc=self.asset_price_mean, scale=self.asset_price_std, size=n_samples
            )
        elif self.model_type == "constant":
            asset_price = np.ones(n_samples) * self.asset_price_mean

        elif self.model_type == "empirical":
            asset_price = self.kde_model.sample(n_samples).reshape(-1)
        return asset_price
