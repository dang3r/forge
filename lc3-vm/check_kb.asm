.ORIG x3000
    AND R0, R0, #0
    LD R3, ASCII_ZERO   ; Load ASCII offset for '0'

POLL1
    POLL
        LDI R0, KBSR
        BRzp POLL
    LDI R0, KBDR
    OUT
BR POLL1

HALT

ASCII_ZERO .FILL x30
NEWLINE    .FILL x0A       ; ASCII value for newline
KBSR       .FILL xFE00
KBDR       .FILL xFE02

.END