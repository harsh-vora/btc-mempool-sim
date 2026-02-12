_counter = 0


def _next_txid():
    global _counter
    _counter += 1
    return f"tx_{_counter:04d}"


class TxInput:
    def __init__(self, txid, index):
        self.txid = txid
        self.index = index

    def __repr__(self):
        return f"TxInput({self.txid}, {self.index})"


class TxOutput:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"TxOutput({self.value})"


class Transaction:
    def __init__(self, inputs, outputs, fee, size=250, replaceable=False):
        self.txid = _next_txid()
        self.inputs = inputs
        self.outputs = outputs
        self.fee = fee
        self.size = size
        self.replaceable = replaceable

    @property
    def fee_rate(self):
        return self.fee / self.size

    def depends_on(self, txid):
        return any(inp.txid == txid for inp in self.inputs)

    def __repr__(self):
        return f"Transaction({self.txid}, fee={self.fee}, size={self.size})"
