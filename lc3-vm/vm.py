import sys
from typing import List
from enum import IntEnum, auto
import termios
import select
import signal
import atexit


class Register(IntEnum):
    R_R0 = 0
    R_R1 = auto()
    R_R2 = auto()
    R_R3 = auto()
    R_R4 = auto()
    R_R5 = auto()
    R_R6 = auto()
    R_R7 = auto()
    R_PC = auto()
    R_COND = auto()
    R_COUNT = auto()


class Opcodes(IntEnum):
    OP_BR = 0  # branch
    OP_ADD = auto()  # add
    OP_LD = auto()  # load
    OP_ST = auto()  # store
    OP_JSR = auto()  # jump
    OP_AND = auto()  # bitwise and
    OP_LDR = auto()  # load register
    OP_STR = auto()  # store register
    OP_RTI = auto()  # unused?
    OP_NOT = auto()  # bitwise not
    OP_LDI = auto()  # load indirect
    OP_STI = auto()  # store indirect
    OP_JMP = auto()  # jump
    OP_RES = auto()  # unused
    OP_LEA = auto()  # load effective address
    OP_TRAP = auto()  # execute trap?


class ConditionFlags:
    FL_POS = 1
    FL_ZRO = 2
    FL_NEG = 4


class Trapcodes(IntEnum):
    TRAP_GETC = 0x20  # get char from keyboard
    TRAP_OUT = auto()  # print a character
    TRAP_PUTS = auto()  # print a word
    TRAP_IN = auto()  # get character and print
    TRAP_PUTSP = auto()  # output a byte string
    TRAP_HALT = auto()  # halt


class MemoryMappedRegisters(IntEnum):
    MR_KBSR = 0xFE00
    MR_KBDR = 0xFE02


class Memory:
    def __init__(self, mem_size: int = 2**16):
        self.mem_size = mem_size
        self.ram = [0 for _ in range(mem_size)]

    def __getitem__(self, address) -> int:
        # TODO: Kludge to cooerce addresses to be uint16
        address = address & 0xFFFF
        if address == MR.MR_KBSR:
            if check_key():
                self.ram[MR.MR_KBSR] = 1 << 15
                self.ram[MR.MR_KBDR] = ord(get_char())
            else:
                self.ram[MR.MR_KBSR] = 0
        return self.ram[address]

    def __setitem__(self, address: int, val: int) -> None:
        # TODO: Kludge to cooerce addresses to be uint16
        address = address & 0xFFFF
        assert 0 <= address < self.mem_size
        self.ram[address] = val & 0xFFFF


class Registers:
    def __init__(self, size: int = Register.R_COUNT):
        self.size = size
        self.r = [0 for _ in range(R.R_COUNT)]

    def __getitem__(self, reg_idx: int) -> int:
        return self.r[reg_idx]

    def __setitem__(self, reg_idx: int, val: int) -> int:
        assert 0 <= reg_idx < self.size
        self.r[reg_idx] = val & 0xFFFF


PC_START: int = 0x3000
R = Register
OP = Opcodes
FL = ConditionFlags
T = Trapcodes
MR = MemoryMappedRegisters
MEM_SIZE = 2**16
MEM = Memory(MEM_SIZE)
REG = Registers(R.R_COUNT)
original_tio = None


def handle_interrupt(signum, frame):
    """Handle Ctrl+C by restoring terminal settings and exiting"""
    restore_input_buffering()
    sys.exit(-2)


def disable_input_buffering():
    """
    Configures terminal for raw input by:
    1. Disabling canonical mode (input is processed character by character)
    2. Disabling echo (typed characters aren't displayed)
    """
    global original_tio
    fd = sys.stdin.fileno()
    original_tio = termios.tcgetattr(fd)
    new_tio = termios.tcgetattr(fd)
    new_tio[3] = new_tio[3] & ~(termios.ICANON | termios.ECHO)  # 3 is c_lflag
    termios.tcsetattr(fd, termios.TCSANOW, new_tio)


def restore_input_buffering():
    """
    Restores the terminal to its original settings
    """
    global original_tio
    if original_tio:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, original_tio)


def check_key():
    """
    Checks if there's input available to read from stdin without blocking.
    Returns True if there's input ready, False otherwise.
    """
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    return bool(ready)


def sign_extend(val: int, bit_count: int) -> int:
    if (val >> (bit_count - 1)) & 1:
        val |= 0xFFFF << bit_count
    return val & 0xFFFF


def update_flags(r) -> None:
    if REG[r] == 0:
        REG[R.R_COND] = FL.FL_ZRO
    elif REG[r] >> 15:
        REG[R.R_COND] = FL.FL_NEG
    elif REG[r] > 0:
        REG[R.R_COND] = FL.FL_POS
    else:
        raise ValueError(f"Register value {r} is not in one of the buckets")


def get_char() -> str:
    import termios, sys, tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch.encode("ascii")


def read_image_file(fname: str) -> None:
    with open(fname, "rb") as f:
        origin = int.from_bytes(f.read(2), byteorder="big")

        max_read = MEM_SIZE - origin
        p_bytes = f.read()
        if len(p_bytes) > max_read:
            raise ValueError(
                f"Program is larger than available memory! program_size={p_bytes} memory_size={MEM_SIZE}"
            )
        for i in range(0, len(p_bytes), 2):
            slot = int.from_bytes(p_bytes[i : i + 2], byteorder="big")
            idx = i // 2
            MEM[origin + idx] = slot


def main():
    # Register the interrupt handler for Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, handle_interrupt)

    # Register cleanup function to run on program exit
    atexit.register(restore_input_buffering)

    # Configure terminal for raw input
    disable_input_buffering()

    if len(sys.argv) < 2:
        print("Usage: lc3 [image-file] ...")
        restore_input_buffering()
        sys.exit(1)

    for image_file in sys.argv[1:]:
        read_image_file(image_file)

    REG[R.R_COND] = FL.FL_ZRO
    REG[R.R_PC] = PC_START

    running = True
    while running:
        if not (0 <= REG[R.R_PC] < MEM_SIZE):
            print(f"Error: PC out of bounds: {REG[R.R_PC]:04x}")
            break

        instr: int = MEM[REG[R.R_PC]]
        op: int = instr >> 12

        # print(f"PC={REG[R.R_PC]:04x} INSTR={instr:04x} OP={op:x}")  # Add debug logging

        REG[R.R_PC] += 1

        if op == OP.OP_ADD:
            dr = (instr >> 9) & 7
            sr1 = (instr >> 6) & 7
            bit_5 = instr >> 5 & 1
            if bit_5:
                imm5 = instr & 0x1F
                imm5 = sign_extend(imm5, 5)
                REG[dr] = REG[sr1] + imm5
            else:
                sr2 = instr & 7
                REG[dr] = REG[sr1] + REG[sr2]
            update_flags(dr)
        elif op == OP.OP_AND:
            dr = (instr >> 9) & 0b111
            sr1 = (instr >> 6) & 0b111
            bit_5 = instr >> 5 & 0b1
            if bit_5:
                imm5 = instr & 0b11111
                imm5 = sign_extend(imm5, 5)
                REG[dr] = REG[sr1] & imm5
            else:
                sr2 = instr & 0b111
                REG[dr] = REG[sr1] & REG[sr2]
            REG[dr] = REG[dr]
            update_flags(dr)
        elif op == OP.OP_NOT:
            dr = (instr >> 9) & 7
            sr = (instr >> 6) & 7
            complement = REG[sr] ^ 0xFFFF
            REG[dr] = complement
            update_flags(dr)
        elif op == OP.OP_BR:
            n = instr >> 11 & 1
            z = instr >> 10 & 1
            p = instr >> 9 & 1
            conditions = [
                n and REG[R.R_COND] == FL.FL_NEG,
                z and REG[R.R_COND] == FL.FL_ZRO,
                p and REG[R.R_COND] == FL.FL_POS,
            ]
            if any(conditions):
                offset = sign_extend(instr & 0x1FF, 9)
                REG[R.R_PC] = REG[R.R_PC] + offset
        elif op == OP.OP_JMP:
            base_r = (instr >> 6) & 7
            REG[R.R_PC] = REG[base_r]
        elif op == OP.OP_JSR:
            bit_11 = instr >> 11 & 1
            REG[R.R_R7] = REG[R.R_PC]
            if bit_11:
                offset = instr & 0x7FF
                REG[R.R_PC] += sign_extend(offset, 11)
            else:
                base_r = (instr >> 6) & 7
                REG[R.R_PC] = REG[base_r]
        elif op == OP.OP_LD:
            dr = instr >> 9 & 7
            offset = sign_extend(instr & 0x1FF, 9)
            REG[dr] = MEM[REG[R.R_PC] + offset]
            update_flags(dr)
        elif op == OP.OP_LDI:
            dr = (instr >> 9) & 0b111
            pc_offset = sign_extend(instr & 0x1FF, 9)
            value = MEM[MEM[REG[R.R_PC] + pc_offset]]
            REG[dr] = value
            update_flags(dr)
        elif op == OP.OP_LDR:
            dr = (instr >> 9) & 7
            base_r = (instr >> 6) & 7
            offset = sign_extend(instr & 0x3F, 6)
            REG[dr] = MEM[REG[base_r] + offset]
            update_flags(dr)
        elif op == OP.OP_LEA:
            dr = (instr >> 9) & 7
            offset = sign_extend(instr & 0x1FF, 9)
            REG[dr] = REG[R.R_PC] + offset
            update_flags(dr)
        elif op == OP.OP_ST:
            sr = (instr >> 9) & 7
            offset = sign_extend(instr & 0x1FF, 9)
            MEM[REG[R.R_PC] + offset] = REG[sr]
        elif op == OP.OP_STI:
            sr = (instr >> 9) & 7
            offset = sign_extend(instr & 0x1FF, 9)
            MEM[MEM[REG[R.R_PC] + offset]] = REG[sr]
        elif op == OP.OP_STR:
            sr = (instr >> 9) & 7
            base_r = (instr >> 6) & 7
            offset = sign_extend(instr & 0x3F, 6)
            MEM[REG[base_r] + offset] = REG[sr]
        elif op == OP.OP_TRAP:
            REG[R.R_R7] = REG[R.R_PC]
            t_code = instr & 0xFF
            if t_code == T.TRAP_GETC:
                char = get_char()
                REG[R.R_R0] = 0
                REG[R.R_R0] = ord(char)
                update_flags(R.R_R0)
            elif t_code == T.TRAP_OUT:
                char = chr(REG[R.R_R0] & 0xFF)
                print(char, end="")
            elif t_code == T.TRAP_PUTS:
                pt = REG[R.R_R0]
                while MEM[pt]:
                    print(chr(MEM[pt]), end="")
                    pt += 1
            elif t_code == T.TRAP_IN:
                char = get_char()
                REG[R.R_R0] = 0
                REG[R.R_R0] = ord(char)
                update_flags(R.R_R0)
            elif t_code == T.TRAP_PUTSP:
                start = REG[R.R_R0]
                while MEM[start]:
                    left = MEM[start] >> 8
                    right = MEM[start] & 0xFF
                    print(chr(left), end="")
                    if right:
                        print(chr(right), end="")
                    start += 1
            elif t_code == T.TRAP_HALT:
                print("HALT!")
                running = False
            else:
                print("WTF")
        elif op == OP.OP_RES or op == OP.OP_RTI:
            pass
        else:
            pass

    restore_input_buffering()


if __name__ == "__main__":
    main()
