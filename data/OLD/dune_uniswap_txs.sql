WITH uniswap_contracts AS (
    SELECT DISTINCT blockchain,
        version,
        project_contract_address
    FROM dex.trades
    WHERE date(block_time) between date('2024-05-01') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
        AND project = 'uniswap'
),
filtered_txs AS (
    SELECT blockchain,
        block_time,
        hash AS tx_hash,
        "from" AS tx_sender,
        to AS tx_receiver,
        gas_used,
        effective_gas_price,
        success
    From evms.transactions
    WHERE date(block_time) between date('2024-05-01') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
)
SELECT *
FROM filtered_txs
    INNER JOIN uniswap_contracts ON filtered_txs.tx_receiver = uniswap_contracts.project_contract_address