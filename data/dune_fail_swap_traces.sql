--Dune query ID: 4021874
WITH raw_swap_traces AS (
    SELECT DISTINCT blockchain,
        tx_hash,
        trace_address
    FROM evms.traces_decoded
    WHERE date(block_time) between date('2024-07-31') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
        AND function_name = 'swap'
),
filtered_txs AS (
    SELECT blockchain,
        hash AS tx_hash,
        gas_used AS gas_units_used_tx
    From evms.transactions
    WHERE date(block_time) between date('2024-07-31') AND date('2024-08-01')
        AND blockchain in ('zksync', 'arbitrum', 'base', 'optimism')
),
swap_traces AS (
    SELECT raw_swap_traces.blockchain,
        raw_swap_traces.tx_hash,
        trace_address,
        gas_units_used_tx
    FROM raw_swap_traces
        LEFT JOIN filtered_txs ON raw_swap_traces.blockchain = filtered_txs.blockchain
        AND raw_swap_traces.tx_hash = filtered_txs.tx_hash
)
SELECT all_traces.blockchain,
    block_time,
    all_traces.tx_hash,
    gas_units_used_tx,
    all_traces.trace_address,
    gas AS gas_trace,
    gas_used AS gas_units_used_trace,
    error
FROM evms.traces as all_traces
    INNER JOIN swap_traces ON all_traces.blockchain = swap_traces.blockchain
    AND all_traces.tx_hash = swap_traces.tx_hash
    AND all_traces.trace_address = swap_traces.trace_address
WHERE tx_success = false
    AND error != 'out of gas'