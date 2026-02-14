import unittest
from transaction import TxInput, TxOutput, Transaction
from utxo import UTXOSet
from mempool import Mempool
from miner import BlockAssembler


class TestUTXOSet(unittest.TestCase):

    def test_valid_tx_accepted(self):
        utxo = UTXOSet()
        utxo.add("fund", 0, 1000)
        tx = Transaction([TxInput("fund", 0)], [TxOutput(800)], fee=200)
        valid, err = utxo.validate_transaction(tx)
        assert valid, f"expected valid, got: {err}"

    def test_missing_input_rejected(self):
        utxo = UTXOSet()
        tx = Transaction([TxInput("nope", 0)], [TxOutput(100)], fee=50)
        valid, _ = utxo.validate_transaction(tx)
        assert not valid

    def test_insufficient_funds_rejected(self):
        utxo = UTXOSet()
        utxo.add("fund", 0, 100)
        tx = Transaction([TxInput("fund", 0)], [TxOutput(200)], fee=50)
        valid, _ = utxo.validate_transaction(tx)
        assert not valid

    def test_apply_consumes_inputs(self):
        utxo = UTXOSet()
        utxo.add("fund", 0, 1000)
        tx = Transaction([TxInput("fund", 0)], [TxOutput(900)], fee=100)
        utxo.apply_transaction(tx)
        assert not utxo.has("fund", 0)
        assert utxo.has(tx.txid, 0)

    def test_clone_is_independent(self):
        utxo = UTXOSet()
        utxo.add("fund", 0, 500)
        clone = utxo.clone()
        utxo.add("fund", 1, 300)
        assert not clone.has("fund", 1)


class TestMempool(unittest.TestCase):

    def _make_utxo(self, entries):
        utxo = UTXOSet()
        for txid, idx, val in entries:
            utxo.add(txid, idx, val)
        return utxo

    def test_valid_tx_added(self):
        utxo = self._make_utxo([("f", 0, 1000)])
        mp = Mempool()
        tx = Transaction([TxInput("f", 0)], [TxOutput(800)], fee=200)
        ok, _ = mp.add_transaction(tx, utxo)
        assert ok
        assert tx.txid in mp.tx_pool

    def test_invalid_tx_rejected(self):
        utxo = UTXOSet()
        mp = Mempool()
        tx = Transaction([TxInput("nope", 0)], [TxOutput(100)], fee=50)
        ok, _ = mp.add_transaction(tx, utxo)
        assert not ok

    def test_rbf_replaces_lower_fee(self):
        utxo = self._make_utxo([("f", 0, 1000)])
        mp = Mempool()
        tx1 = Transaction([TxInput("f", 0)], [TxOutput(800)], fee=200, size=250, replaceable=True)
        mp.add_transaction(tx1, utxo)

        tx2 = Transaction([TxInput("f", 0)], [TxOutput(600)], fee=400, size=250)
        ok, _ = mp.add_transaction(tx2, utxo)
        assert ok
        assert tx1.txid not in mp.tx_pool
        assert tx2.txid in mp.tx_pool

    def test_rbf_rejected_if_not_replaceable(self):
        utxo = self._make_utxo([("f", 0, 1000)])
        mp = Mempool()
        tx1 = Transaction([TxInput("f", 0)], [TxOutput(800)], fee=200, replaceable=False)
        mp.add_transaction(tx1, utxo)

        tx2 = Transaction([TxInput("f", 0)], [TxOutput(600)], fee=400)
        ok, _ = mp.add_transaction(tx2, utxo)
        assert not ok

    def test_eviction_removes_lowest_fee_rate(self):
        utxo = self._make_utxo([("f", i, 1000) for i in range(3)])
        mp = Mempool(max_size=500)

        tx_low = Transaction([TxInput("f", 0)], [TxOutput(900)], fee=100, size=200)   # 0.50
        tx_mid = Transaction([TxInput("f", 1)], [TxOutput(700)], fee=300, size=200)   # 1.50
        mp.add_transaction(tx_low, utxo)
        mp.add_transaction(tx_mid, utxo)

        tx_high = Transaction([TxInput("f", 2)], [TxOutput(500)], fee=500, size=200)  # 2.50
        mp.add_transaction(tx_high, utxo)

        assert tx_low.txid not in mp.tx_pool, "lowest fee_rate tx should be evicted"
        assert tx_mid.txid in mp.tx_pool
        assert tx_high.txid in mp.tx_pool


class TestBlockAssembly(unittest.TestCase):

    def test_prioritizes_higher_fee_rate(self):
        utxo = UTXOSet()
        for i in range(3):
            utxo.add("f", i, 1000)

        mp = Mempool()
        tx_low = Transaction([TxInput("f", 0)], [TxOutput(900)], fee=100, size=300)
        tx_high = Transaction([TxInput("f", 1)], [TxOutput(500)], fee=500, size=300)
        tx_mid = Transaction([TxInput("f", 2)], [TxOutput(700)], fee=300, size=300)

        for tx in [tx_low, tx_high, tx_mid]:
            mp.add_transaction(tx, utxo)

        block = BlockAssembler().assemble_block(mp, utxo, max_block_size=700)

        assert len(block.transactions) == 2
        assert block.transactions[0].txid == tx_high.txid
        assert block.transactions[1].txid == tx_mid.txid

    def test_block_respects_size_limit(self):
        utxo = UTXOSet()
        utxo.add("f", 0, 1000)
        utxo.add("f", 1, 1000)

        mp = Mempool()
        tx1 = Transaction([TxInput("f", 0)], [TxOutput(800)], fee=200, size=500)
        tx2 = Transaction([TxInput("f", 1)], [TxOutput(800)], fee=200, size=500)
        mp.add_transaction(tx1, utxo)
        mp.add_transaction(tx2, utxo)

        block = BlockAssembler().assemble_block(mp, utxo, max_block_size=600)
        assert block.total_size <= 600


if __name__ == "__main__":
    unittest.main()
