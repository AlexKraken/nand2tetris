import sys
import os

INPUT_STREAM = sys.argv[1]

ARITHMETIC_COMMANDS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
PUSHPOP_COMMANDS = {"push", "pop"}
SEGMENTS = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "temp": "R",
}

label_count = 0


def increment_stackpointer() -> str:
    """ "Returns the code for incrementing the stack pointer"""
    return "\n".join(["@SP", "M=M+1", ""])


def decrement_stackpointer() -> str:
    return "\n".join(["@SP", "M=M-1"])


def load_stackpointer_to_A() -> str:
    return "\n".join([decrement_stackpointer(), "A=M"])


def push_D_to_stack() -> str:
    return "\n".join(
        [
            "@SP",
            "A=M",
            "M=D",
            increment_stackpointer(),
        ]
    )


def pop_stack_to_D() -> str:
    return "\n".join([load_stackpointer_to_A(), "D=M"])


def write_compare(command: str) -> str:
    jump = "J" + command.upper()
    global label_count
    label_count = label_count + 1
    return "\n".join(
        [
            pop_stack_to_D(),
            load_stackpointer_to_A(),
            "D=M-D",
            f"@LABEL.{label_count}",
            f"D;{jump}",
            "@SP",
            "A=M",
            "M=0",
            f"@ENDLABEL.{label_count}",
            "0;JMP",
            f"(LABEL.{label_count})",
            "@SP",
            "A=M",
            "M=-1",
            f"(ENDLABEL.{label_count})",
            increment_stackpointer(),
        ]
    )


def write_arithmetic(command: str) -> str:
    match command:
        case "add":
            return "\n".join(
                [
                    pop_stack_to_D(),
                    load_stackpointer_to_A(),
                    "M=D+M",
                    increment_stackpointer(),
                ]
            )

        case "sub":
            return "\n".join(
                [
                    pop_stack_to_D(),
                    load_stackpointer_to_A(),
                    "M=M-D",
                    increment_stackpointer(),
                ]
            )
        case "neg":
            return "\n".join(
                [
                    load_stackpointer_to_A(),
                    "M=-M",
                    increment_stackpointer(),
                ]
            )
        case "eq" | "gt" | "lt":
            return write_compare(command)
        case "and":
            return "\n".join(
                [
                    pop_stack_to_D(),
                    load_stackpointer_to_A(),
                    "M=D&M",
                    increment_stackpointer(),
                ]
            )
        case "or":
            return "\n".join(
                [
                    pop_stack_to_D(),
                    load_stackpointer_to_A(),
                    "M=D|M",
                    increment_stackpointer(),
                ]
            )
        case "not":
            return "\n".join(
                [
                    load_stackpointer_to_A(),
                    "M=!M",
                    increment_stackpointer(),
                ]
            )
        case _:
            return f"\n{command}\n"


def load_segment(segment: str, index: int) -> str:

    return "\n".join(
        [
            f"@{segment}",
            "D=M",
            f"@{index}",
            "A=D+A",
        ]
    )


def write_pushpop(command: str, segment: str, index: int) -> str:

    match command:

        case "pop":
            if segment == "temp":
                return "\n".join(
                    [
                        f"@R{5 + int(index)}",
                        "D=A",
                        f"@R{5 + int(index)}",
                        "M=D",
                        pop_stack_to_D(),
                        f"@R{5 + int(index)}",
                        "A=M",
                        "M=D",
                        "",
                    ]
                )
            elif segment == "pointer":
                return "\n".join(
                    [
                        f"@R{3 + int(index)}",
                        "D=A",
                        f"@R{3 + int(index)}",
                        "M=D",
                        pop_stack_to_D(),
                        f"@R{3 + int(index)}",
                        "A=M",
                        "M=D",
                        "",
                    ]
                )
            elif segment == "static":
                return "\n".join(
                    [
                        f"@STATIC.{int(index)}",
                        "D=A",
                        f"@STATIC.{int(index)}",
                        "M=D",
                        pop_stack_to_D(),
                        f"@STATIC.{int(index)}",
                        "A=M",
                        "M=D",
                        "",
                    ]
                )
            return "\n".join(
                [
                    load_segment(SEGMENTS[segment], index),
                    "D=A",
                    "@R13",
                    "M=D",
                    pop_stack_to_D(),
                    "@R13",
                    "A=M",
                    "M=D",
                    "",
                ]
            )

        case "push":
            if segment == "constant":
                return "\n".join(
                    [
                        f"@{index}",
                        "D=A",
                        "@SP",
                        "A=M",
                        "M=D",
                        increment_stackpointer(),
                    ]
                )
            elif segment == "temp":
                return "\n".join(
                    [
                        f"@R{5 + int(index)}",
                        "D=M",
                        push_D_to_stack(),
                    ]
                )
            elif segment == "pointer":
                return "\n".join(
                    [
                        f"@R{3 + int(index)}",
                        "D=M",
                        push_D_to_stack(),
                    ]
                )
            elif segment == "static":
                return "\n".join(
                    [
                        f"@STATIC.{int(index)}",
                        "D=M",
                        push_D_to_stack(),
                    ]
                )
            else:
                return "\n".join(
                    [
                        load_segment(SEGMENTS[segment], index),
                        "D=M",
                        push_D_to_stack(),
                    ]
                )

        case _:
            return f"\n{command} {segment} {index}\n"


if os.path.isdir(INPUT_STREAM):
    directory_list = os.listdir(INPUT_STREAM)

    for file in directory_list:

        if file.endswith(".vm"):
            vm_path = os.path.join(INPUT_STREAM, file)
            asm_path = vm_path[:-2] + "asm"

            with open(vm_path, "r") as reader:
                with open(asm_path, "w") as writer:
                    for line in reader:
                        command = line.strip().split(None, 3)
                        if command != [] and command != [""]:
                            # writer.write(f"// {command=}\n")
                            if command[0] in ARITHMETIC_COMMANDS:
                                writer.write(write_arithmetic(command[0]))

                            elif command[0] in PUSHPOP_COMMANDS:
                                writer.write(
                                    write_pushpop(command[0], command[1], command[2])
                                )
