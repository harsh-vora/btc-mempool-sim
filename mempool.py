class Mempool:
    def __init__(self, max_size=5_000_000):
        self.tx_pool = {}
        self.max_size = max_size
        self.current_size = 0

    def _find_conflicts(self, tx):
        """Find existing txs that spend the same inputs."""
        new_inputs = {(inp.txid, inp.index) for inp in tx.inputs}
        conflicts = []
        for existing in self.tx_pool.values():
            existing_inputs = {(inp.txid, inp.index) for inp in existing.inputs}
            if new_inputs & existing_inputs:
                conflicts.append(existing)
        return conflicts

    def _evict(self):
        while self.current_size > self.max_size and self.tx_pool:
            worst = min(self.tx_pool.values(), key=lambda tx: tx.fee_rate)
            self.remove_transaction(worst.txid)

    def add_transaction(self, tx, utxo_set):
        if tx.txid in self.tx_pool:
            return False, "already in mempool"

        # check for RBF conflicts
        conflicts = self._find_conflicts(tx)
        for conflict in conflicts:
            if not conflict.replaceable:
                return False, f"conflicts with non-replaceable tx {conflict.txid}"
            if tx.fee_rate <= conflict.fee_rate:
                return False, f"fee rate not higher than {conflict.txid}"

        valid, err = utxo_set.validate_transaction(tx)
        if not valid:
            return False, err

        # evict conflicting txs
        for conflict in conflicts:
            self.remove_transaction(conflict.txid)

        self.tx_pool[tx.txid] = tx
        self.current_size += tx.size

        # evict lowest fee_rate txs if over limit
        self._evict()

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
