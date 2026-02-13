class Block:
    def __init__(self, transactions=None):
        self.transactions = transactions or []
        self.total_size = sum(tx.size for tx in self.transactions)
        self.total_fees = self.calculate_total_fees()

    def calculate_total_fees(self):
        return sum(tx.fee for tx in self.transactions)

    def add_transaction(self, tx):
        self.transactions.append(tx)
        self.total_size += tx.size
        self.total_fees += tx.fee

    def __repr__(self):
        return f"Block({len(self.transactions)} txs, {self.total_size} bytes, fees={self.total_fees})"
