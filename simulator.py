import random
from transaction import TxInput, TxOutput, Transaction
from utxo import UTXOSet
from mempool import Mempool
from miner import BlockAssembler


def seed_utxos(utxo_set, count=20):
    for i in range(count):
        value = random.randint(500, 5000)
        utxo_set.add("coinbase", i, value)


def generate_transactions(utxo_set, count=10):
    available = list(utxo_set.utxos.items())
    random.shuffle(available)

    txs = []
    for (txid, index), value in available[:count]:
        fee = random.randint(50, 500)
        size = random.randint(150, 600)
        out_value = value - fee
        if out_value <= 0:
            continue
        tx = Transaction(
            inputs=[TxInput(txid, index)],
            outputs=[TxOutput(out_value)],
            fee=fee,
            size=size,
            replaceable=random.choice([True, False]),
        )
        txs.append(tx)
    return txs


def main():
    random.seed(42)

    utxo_set = UTXOSet()
    seed_utxos(utxo_set)

    txs = generate_transactions(utxo_set, count=15)

    mempool = Mempool()
    for tx in txs:
        ok, err = mempool.add_transaction(tx, utxo_set)
        status = "accepted" if ok else f"rejected ({err})"
        print(f"  {tx.txid}: fee_rate={tx.fee_rate:.3f} -> {status}")

    print(f"\nMempool: {mempool}")

    assembler = BlockAssembler()
    block = assembler.assemble_block(mempool, utxo_set, max_block_size=4000)

    print(f"\nAssembled block: {block}")
    print("Transactions in block:")
    for tx in block.transactions:
        print(f"  {tx.txid}: fee={tx.fee}, size={tx.size}, fee_rate={tx.fee_rate:.3f}")

    print(f"\nTotal fees: {block.total_fees}")
    print(f"Block size: {block.total_size} bytes")


if __name__ == "__main__":
    main()
