.ORIG x3000
    AND R0, R0, #0
    LD R3, ASCII_ZERO   ; Load ASCII offset for '0'

POLL1
    ; The 15th-bit is set to `1` when there is KB input. Thus, condition register will be negative
    ; We only ever set it to 0 or 1<<15, never > 0
    POLL
        LDI R0, KBSR
        BRz POLL
    LDI R0, KBDR
    OUT
BR POLL1

HALT

ASCII_ZERO .FILL x30
NEWLINE    .FILL x0A       ; ASCII value for newline
KBSR       .FILL xFE00
KBDR       .FILL xFE02

.END