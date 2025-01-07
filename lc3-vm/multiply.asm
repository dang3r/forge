.ORIG x3000

LD R0, MOP1
LD R1, MOP2

; Multiply
JSR MULT
ADD R0, R2, #0
OUT

; DIvide
JSR DIV
;ADD R0, R3, #0
;OUT
;ADD R0, R4, #0
;OUT

; Print 10 in reverse order
JSR PRINT

HALT

; MULTIPLY (R0*R1)
; Arguments: R0, R1
; Return: R2=R0*R1
MULT
    LEA R6, MULT_REG
    STR R0, R6, #0
    STR R1, R6, #1
    STR R3, R6, #3
    STR R4, R6, #4
    STR R5, R6, #5

    AND R2, R2, #0
    MULT_LOOP
        ADD R2, R2, R0
        ADD R1, R1, #-1
    BRp MULT_LOOP

    LDR R0, R6, #0
    LDR R1, R6, #1
    LDR R3, R6, #3
    LDR R4, R6, #4
    LDR R5, R6, #5

    RET;

; Divide (R0/R1)
; Arguments: R0, R1 
; Return: R3 (quotient), R4 Modulus
DIV
    ; save registers
    LEA R6, DIV_REG
    STR R0, R6, #0
    STR R1, R6, #1
    STR R2, R6, #2
    STR R3, R6, #3
    STR R4, R6, #4
    STR R5, R6, #5

    AND R3, R3, #0  ; R3=0 quotient
    AND R4, R4, #0  ; R4=0  remainder/modulus
    NOT R5, R1      ; -divisor
    ADD R5, R5, #1  ;

    ADD R4, R0, R5
    BRn GREATER
        ; if a >= b, return a//b, a%b
        DIV_LOOP
            ADD R3, R3, #1
            ADD R0, R0, R5
            ADD R6, R0, R5
        BRzp DIV_LOOP
        ADD R4, R0, #0
        BR DIV_END
    ; if b > a, return 0, a
    GREATER
        AND R3, R3, #0
        ADD R4, R0, #0
    DIV_END

    ; load registers
    LEA R6, DIV_REG
    LDR R0, R6, #0
    LDR R1, R6, #1
    LDR R2, R6, #2
    LDR R5, R6, #5
    RET

; Print a number to stdout (R0)
; Arguments: R0
PRINT
    LEA R6, PRINT_REG
    STR R0, R6, #0
    STR R1, R6, #1
    STR R2, R6, #2
    STR R3, R6, #3
    STR R4, R6, #4
    STR R5, R6, #5

    ; Set R1=10
    AND R1, R1, #0
    ADD R1, R1, #10
    PR_LOOP
        ; R3 = R0 // 10
        ; R4 = R0 % 10
        JSR DIV
        LD R2, ASCII_ZERO
        ADD R0, R4, R2
        OUT

        ADD R0, R3, #0
        BRz PR_END
        BRp PR_LOOP
        BRn PR_END
    PR_END
    

    LDR R0, R6, #0
    LDR R1, R6, #1
    LDR R2, R6, #2
    LDR R3, R6, #3
    LDR R4, R6, #4
    LDR R5, R6, #5
    RET
    

; Data Section
MOP1 .FILL x000a
MOP2 .FILL x000b
ASCII_ZERO .FILL x30
PRINT_REG .BLKW 8
MULT_REG .BLKW 8
DIV_REG .BLKW 8