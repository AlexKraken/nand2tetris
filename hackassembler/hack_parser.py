from hack_code import HackCode
from symbol_table import SymbolTable


class HackParser:
    def __init__(self, asm_path) -> None:

        self.symbol_table = SymbolTable()
        self.loop_list = {}

        with open(asm_path, "r") as reader:
            line_count = 0
            for line in reader:

                loop = line.find("(")
                if loop == 0:
                    name = line[1 : line.find(")")]
                    self.symbol_table.add_loop(name, line_count)
                    line_count = line_count - 1

                instruction = self.remove_comments(line).strip()
                if instruction != "":
                    line_count = line_count + 1

            hack_path = asm_path[:-3] + "hack"
            with open(hack_path, "w") as writer:
                reader.seek(0)

                for line in reader:
                    instruction = self.remove_comments(line).strip()
                    at = instruction.find("@")

                    if at > -1:
                        writer.writelines(self.binary(instruction[1:]) + "\n")
                    elif instruction != "" and instruction[0] != "(":
                        writer.writelines("111" + self.fields(instruction) + "\n")

    def binary(self, line: str) -> str:
        address = int(line) if line.isdigit() else self.symbol_table.get_address(line)
        return format(address, "016b")

    def fields(self, instruction: str) -> str:
        dest = comp = jump = ""
        equals = instruction.find("=")
        semicolon = instruction.find(";")

        if equals > -1:
            dest = instruction[:equals]
            comp = instruction[equals + 1 :]
        if semicolon > -1:
            jump = instruction[-3:]
            comp = comp[:-4] if equals > -1 else instruction[:semicolon]

        return HackCode.comp(comp) + HackCode.dest(dest) + HackCode.jump(jump)

    def remove_comments(self, line: str) -> str:
        return line[: line.find("/")]
