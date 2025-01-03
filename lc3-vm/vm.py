import sys
from typing import List
from enum import IntEnum, auto

MEM_SIZE: int = 2**16
MEM: List[int] = [0 for _ in range(MEM_SIZE)]
PC_START: int = 0x3000


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


R = Register

REG: List[int] = [0 for _ in range(R.R_COUNT)]


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


OP = Opcodes


class ConditionFlags:
    FL_POS = 1
    FL_ZRO = 2
    FL_NEG = 4


FL = ConditionFlags


def sign_extend(val: int, bit_count: int) -> int:
    # 5 bits: 0b11111 is -1
    # 8 bits:0b11111 -> 0b11111111
    if val & (1 << bit_count):
        one_bits = 16 - bit_count
        val |= 2 ^ (one_bits - 1)

    return val


def update_flags(r) -> None:
    if REG[r] == 0:
        REG[R.R_COND] = FL.FL_ZRO
    elif REG[r] >> 15:
        REG[R.R_COND] = FL.FL_NEG
    elif REG[r] > 0:
        REG[R.R_COND] = FL.FL_POS
    else:
        raise ValueError(f"Register value {r} is not in one of the buckets")


def cutoff_bits(val: int) -> int:
    return val & 0xFFFF


def main():
    if len(sys.argv) < 2:
        print("Usage: lc3 [image-file] ...")
        sys.exit(1)

    for image_file in sys.argv[2:]:
        pass

    REG[R.R_COND] = FL.FL_ZRO
    REG[R.R_PC] = PC_START

    running = True
    while running:

        instr: int = REG[R.R_PC]
        REG[R.R_PC] += 1
        op: int = instr >> 12

        if op == OP.OP_ADD:
            dr = (instr >> 9) & 0b111
            sr1 = (instr >> 6) & 0b111
            bit_5 = instr >> 5 & 0b1
            if bit_5:
                imm5 = instr & 0b11111
                imm5 = sign_extend(imm5)
                REG[dr] = REG[sr1] + imm5
            else:
                sr2 = instr & 0b111
                REG[dr] = REG[sr1] + REG[sr2]
            REG[dr] = cutoff_bits(REG[dr])
            update_flags(dr)
        elif op == OP.OP_AND:
            dr = (instr >> 9) & 0b111
            sr1 = (instr >> 6) & 0b111
            bit_5 = instr >> 5 & 0b1
            if bit_5:
                imm5 = instr & 0b11111
                imm5 = sign_extend(imm5)
                REG[dr] = REG[sr1] & imm5
            else:
                sr2 = instr & 0b111
                REG[dr] = REG[sr1] & sr2
            REG[dr] = cutoff_bits(REG[dr])
            update_flags(dr)
        elif op == OP.OP_NOT:
            dr = (instr >> 9) & 0b111
            sr = (instr >> 6) & 0b111
            complement = REG[sr] ^ 0xFFFF
            REG[dr] = cutoff_bits(complement)
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
                REG[R.R_PC] = R.R_PC + offset
                REG[dr] = cutoff_bits(REG[R.R_PC])
        elif op == OP.OP_JMP:
            base_r = (instr >> 6) & 7
            REG[R.R_PC] = REG[base_r]
        elif op == OP.OP_JSR:
            bit_11 = instr >> 11 & 1
            REG[R.R7] = REG[R.PC]
            if bit_11:
                offset = instr & 0x3FF
                REG[R.R_PC] += sign_extend(offset, 11)
            else:
                base_r = (instr >> 6) & 7
                REG[R.R_PC] = REG[base_r]
            REG[R.R_PC] = cutoff_bits(REG[R.R_PC])
        elif op == OP.OP_LD:
            dr = instr >> 9 & 7
            offset = sign_extend(instr & 0x1FF, 9)
            REG[dr] = cutoff_bits(REG[R.PC] + offset)
            update_flags(dr)
        elif op == OP.OP_LDI:
            dr = (instr >> 9) & 0b111
            pc_offset = sign_extend(instr & 0x1FF, 9)
            value = MEM[cutoff_bits(MEM[R.PC + pc_offset])]
            REG[dr] = cutoff_bits(value)
            update_flags(dr)
        elif op == OP.OP_LDR:
            dr = (instr >> 9) & 7
            base_r = (instr >> 6) & 7
            offset = sign_extend(instr & 0x3F, 6)
            REG[dr] = MEM[cutoff_bits(REG[base_r] + offset)]
            update_flags(dr)
        elif op == OP.OP_LEA:
            dr = (instr >> 9) & 7
            offset = sign_extend(instr & 0x1FF, 9)
            REG[dr] = cutoff_bits(REG[R.R_PC] + offset)
            update_flags(dr)
            pass
        elif op == OP.OP_ST:
            sr = (instr >> 9) & 7
            offset = sign_extend(instr & 0x1FF, 9)
            MEM[cutoff_bits(REG[R.PC] + offset)] = REG[sr]
        elif op == OP.OP_STI:
            sr = (instr >> 9) & 7
            offset = sign_extend(instr & 0x1FF, 9)
            MEM[cutoff_bits(MEM[REG[R.PC] + offset])] = REG[sr]
        elif op == OP.OP_STR:
            sr = (instr >> 9) & 7
            base_r = (instr >> 6) & 7
            offset = sign_extend(instr & 0x3F, 6)
            MEM[cutoff_bits(REG[base_r] + offset)] = REG[sr]
        elif op == OP.OP_TRAP:
            pass
        elif op == OP.OP_RES:
            pass
        elif op == OP.OP_RTI:
            pass
        else:
            pass
