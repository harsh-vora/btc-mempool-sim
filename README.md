# Bitcoin Mempool & Block Assembly Policy Simulator

Policy-layer simulation of Bitcoin mempool behavior and block construction, focusing on transaction admission, fee-rate prioritization, and simplified RBF.

This is an educational project. It does not implement cryptography, script validation, networking, or proof-of-work.

## What Is Modeled

- UTXO-based transaction validation (input existence, value sufficiency)
- Mempool admission with policy checks
- Fee-rate-based transaction prioritization
- Mempool size limits with eviction
- Simplified Replace-By-Fee (RBF)
- Greedy block assembly against a cloned UTXO set

## What Is Simplified

- Transactions use an incremental counter for txid generation instead of hashing
- Outputs carry only a value (no script, no address)
- No signature verification or script execution
- No coinbase transaction in assembled blocks
- No transaction dependency graph or ancestor/descendant tracking
- RBF checks only fee rate and the `replaceable` flag — no absolute fee increase requirement

## Architecture

```
transaction.py   Data types: TxInput, TxOutput, Transaction
utxo.py          Validation layer: UTXOSet
mempool.py       Policy layer: Mempool (admission, RBF, eviction)
block.py         Block container
miner.py         BlockAssembler (greedy block construction)
simulator.py     Entry point: seeds UTXOs, generates txs, runs simulation
tests.py         Unit tests
```

### Validation vs Policy

The UTXO set handles **validation** — whether a transaction is structurally sound (inputs exist, values balance). The mempool handles **policy** — whether a valid transaction should be accepted given current conditions (duplicates, conflicts, capacity).

Block assembly works against a **cloned** UTXO set so the original remains unmodified. Each candidate transaction is validated against the clone before inclusion.

### Fee Prioritization

Transactions are sorted by `fee / size` (fee rate, in satoshis per byte). Block assembly is greedy: pick the highest fee-rate transaction that fits, validate it, apply it to the cloned UTXO set, repeat.

### Eviction

When the mempool exceeds `max_size` (in bytes), the lowest fee-rate transactions are removed until it fits within the limit. No dependency awareness — eviction is purely by individual fee rate.

### Simplified RBF

A new transaction can replace an existing one if:
1. They spend at least one common input
2. The existing transaction has `replaceable=True`
3. The new transaction has a strictly higher fee rate

The conflicting transaction is removed before the replacement is inserted.

## Running

```
python3 simulator.py
python3 -m unittest tests -v
```

## Known Limitations

- No transaction dependency tracking (parent-child relationships ignored during assembly and eviction)
- Block assembly is greedy and doesn't optimize for global fee maximization
- No multi-input conflict graphs for RBF
- No transaction expiry or time-based eviction
- No witness data or segwit weight units
- Deterministic txids are not realistic

## Possible Extensions

- **CPFP (Child Pays For Parent)**: Track ancestor fee rates and allow child transactions to bump parents into blocks
- **Package relay**: Evaluate groups of dependent transactions together for admission
- **Orphan handling**: Hold transactions with missing inputs and re-evaluate when parents arrive
- **Ancestor/descendant limits**: Cap the length and size of transaction chains in the mempool
- **Knapsack block assembly**: Better optimization than greedy selection for fee maximization
