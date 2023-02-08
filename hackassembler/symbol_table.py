class SymbolTable:
    def __init__(self) -> None:
        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576,
        }

        for i in range(16):
            self.table[f"R{i}"] = i

        self.counter = 15

    def add_loop(self, symbol, line_number) -> None:
        self.table[symbol] = line_number

    def get_address(self, symbol) -> int:
        if symbol not in self.table.keys():
            self.increment_counter()
        return self.table.setdefault(symbol, self.counter)

    def increment_counter(self) -> int:
        self.counter += 1
        return self.counter
