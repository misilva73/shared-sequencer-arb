WITH bucket_stats AS (
    SELECT blockchain,
        approx_percentile(gas_price_gwei, 0.99) AS bucket_max
    FROM gas.fees
    WHERE date(block_time) between date('2024-05-01') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
    GROUP BY blockchain
),
gas_data AS (
    SELECT gas.blockchain,
        width_bucket(
            gas_price_gwei,
            0,
            bucket_max,
            1000
        ) as bucket,
        gas_price_gwei
    FROM gas.fees AS gas
        LEFT JOIN bucket_stats on gas.blockchain = bucket_stats.blockchain
    WHERE date(block_time) between date('2024-05-01') AND date('2024-08-01')
        AND gas.blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
)
SELECT blockchain,
    bucket,
    min(gas_price_gwei) as bucket_lower_bound,
    max(gas_price_gwei) as bucket_upper_bound,
    count(*) as bucket_cnt
FROM gas_data
GROUP BY blockchain,
    bucket
ORDER BY bucket