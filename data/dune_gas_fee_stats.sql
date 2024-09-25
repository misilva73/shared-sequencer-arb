SELECT blockchain,
    avg(gas_price_gwei) as avg_gas_price_gwei,
    stddev(gas_price_gwei) as std_gas_price_gwei,
    min(gas_price_gwei) as min_gas_price_gwei,
    approx_percentile(gas_price_gwei, 0.1) AS percentile_10_gas_price_gwei,
    approx_percentile(gas_price_gwei, 0.5) AS median_gas_price_gwei,
    approx_percentile(gas_price_gwei, 0.9) AS percentile_90_gas_price_gwei,
    approx_percentile(gas_price_gwei, 0.95) AS percentile_95_gas_price_gwei,
    approx_percentile(gas_price_gwei, 0.99) AS percentile_99_gas_price_gwei,
    max(gas_price_gwei) as max_gas_price_gwei
FROM gas.fees
WHERE date(block_time) between date('2024-05-01') AND date('2024-08-01')
    AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
GROUP BY blockchain