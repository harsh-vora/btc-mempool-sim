import copy


class UTXOSet:
    def __init__(self):
        self.utxos = {}  # (txid, index) -> value

    def add(self, txid, index, value):
        self.utxos[(txid, index)] = value

    def remove(self, txid, index):
        del self.utxos[(txid, index)]

    def get(self, txid, index):
        return self.utxos.get((txid, index))

    def has(self, txid, index):
        return (txid, index) in self.utxos

    def validate_transaction(self, tx):
        # all inputs must reference existing utxos
        for inp in tx.inputs:
            if not self.has(inp.txid, inp.index):
                return False, f"missing utxo ({inp.txid}, {inp.index})"

        input_sum = sum(self.get(inp.txid, inp.index) for inp in tx.inputs)
        output_sum = sum(out.value for out in tx.outputs)

        if input_sum < output_sum + tx.fee:
            return False, "inputs don't cover outputs + fee"

        return True, None

    def apply_transaction(self, tx):
        valid, err = self.validate_transaction(tx)
        if not valid:
            raise ValueError(f"invalid tx {tx.txid}: {err}")

        # consume inputs
        for inp in tx.inputs:
            self.remove(inp.txid, inp.index)

        # create new outputs
        for i, out in enumerate(tx.outputs):
            self.add(tx.txid, i, out.value)

    def clone(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return f"UTXOSet({len(self.utxos)} utxos)"
