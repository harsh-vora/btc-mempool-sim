class Mempool:
    def __init__(self, max_size=5_000_000):
        self.tx_pool = {}
        self.max_size = max_size
        self.current_size = 0

    def add_transaction(self, tx, utxo_set):
        if tx.txid in self.tx_pool:
            return False, "already in mempool"

        if self.current_size + tx.size > self.max_size:
            return False, "mempool full"

        valid, err = utxo_set.validate_transaction(tx)
        if not valid:
            return False, err

        self.tx_pool[tx.txid] = tx
        self.current_size += tx.size
        return True, None

    def remove_transaction(self, txid):
        if txid not in self.tx_pool:
            return False
        tx = self.tx_pool.pop(txid)
        self.current_size -= tx.size
        return True

    def get_sorted_transactions(self):
        return sorted(self.tx_pool.values(), key=lambda tx: tx.fee_rate, reverse=True)

    def __len__(self):
        return len(self.tx_pool)

    def __repr__(self):
        return f"Mempool({len(self.tx_pool)} txs, {self.current_size}/{self.max_size} bytes)"
