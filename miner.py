from block import Block


class BlockAssembler:
    def assemble_block(self, mempool, utxo_set, max_block_size=1_000_000):
        block = Block()
        utxo_clone = utxo_set.clone()
        candidates = mempool.get_sorted_transactions()

        for tx in candidates:
            if block.total_size + tx.size > max_block_size:
                continue

            valid, _ = utxo_clone.validate_transaction(tx)
            if not valid:
                continue

            utxo_clone.apply_transaction(tx)
            block.add_transaction(tx)

        return block
