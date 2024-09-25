--Dune query ID: 4017799
WITH filtered_swaps AS (
    SELECT blockchain,
        project,
        version,
        token_pair,
        token_bought_symbol,
        token_sold_symbol,
        token_bought_amount,
        token_sold_amount,
        tx_hash,
        evt_index
    FROM dex.trades
    WHERE date(block_time) between date('2024-07-31') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
),
filtered_txs AS (
    SELECT blockchain,
        block_time,
        hash AS tx_hash,
        "from" AS tx_sender,
        to AS tx_receiver,
        gas_used,
        effective_gas_price
    From evms.transactions
    WHERE date(block_time) between date('2024-07-31') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
)
SELECT *
FROM filtered_swaps
    LEFT JOIN filtered_txs ON filtered_txs.blockchain = filtered_swaps.blockchain
    AND filtered_txs.tx_hash = filtered_swaps.tx_hash