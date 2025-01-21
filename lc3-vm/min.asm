.ORIG x3000

STACK_PTR_START .FILL xAFFF

MULT_OP1 .FILL xF
MULT_OP2 .FILL x5

LD R6, STACK_PTR_START

; Multiplication with Stack Pointer
LD R0, MULT_OP1
LD R1, MULT_OP2
ADD R6, R6, #-1
STR R1, R6, #0
ADD R6, R6, #-1
STR R0, R6, #0
JSR MULTNEW
LDR R0, R6, #0
ADD R6, R6, #3

JSR STRINGIFY
AND R0, R0, #0
ADD R0, R1, #0
PUTS
LD R0, NEWLINE
OUT
HALT

; MULTIPLY
; Arguments: a,b
; Return: c=a*b
MULTNEW
    ADD R6, R6, #-1 ; save space for return value
    ADD R6, R6, #-1 ; save space and push previous return address
    STR R7, R6, #0
    ADD R6, R6, #-1 ; save space and push previous frame pointer
    STR R5, R6, #0
    ADD R5, R6, #-1  ; Frame pointer points to first saved variable

    ; Save registers R0, R1, R2
    ADD R6, R6, #-1
    STR R0, R6, #0
    ADD R6, R6, #-1
    STR R1, R6, #0
    ADD R6, R6, #-1
    STR R2, R6, #0

    ; Load in arguments to R0, R1, R2
    LDR R0, R5, #4
    LDR R1, R5, #5
    AND R2, R2, #0

    ; Execute
    MULT_LOOP
        ADD R2, R2, R0
        ADD R1, R1, #-1
    BRp MULT_LOOP

    ; Store return in FP + 3
    STR R2, R5, #3

    ; Load registers R0, R1, R2
    LDR R2, R6, #0
    ADD R6, R6, #1
    LDR R1, R6, #0
    ADD R6, R6, #1
    LDR R0, R6, #0
    ADD R6, R6, #1

    ; Load R5
    LDR R5, R6, #0
    ADD R6, R6, #1

    ; Load R7
    LDR R7, R6, #0
    ADD R6, R6, #1

    RET

; Divide (R0/R1)
; Arguments: R0, R1 
; Return: R3 (quotient), R4 Modulus
DIV
    ; save registers
    LEA R6, DIV_REG
    STR R0, R6, #0
    STR R1, R6, #1
    STR R2, R6, #2
    STR R5, R6, #5
    STR R6, R6, #6
    STR R7, R6, #7

    AND R3, R3, #0  ; R3=0 quotient
    ADD R4, R0, #0  ; R4=R0  remainder/modulus
    NOT R5, R1      ; -divisor
    ADD R5, R5, #1  ;

    ADD R2, R4, R5
    BRn DIV_GREATER
        ; if a >= b, return a//b, a%b
        DIV_LOOP
            ADD R3, R3, #1
            ADD R4, R4, R5
            ADD R2, R4, R5
        BRzp DIV_LOOP
        BR DIV_END
    ; if b > a, return 0, a
    DIV_GREATER
        AND R3, R3, #0
    DIV_END

    ; load registers
    LEA R6, DIV_REG
    LDR R0, R6, #0
    LDR R1, R6, #1
    LDR R2, R6, #2
    LDR R5, R6, #5
    LDR R6, R6, #6
    LDR R7, R6, #7
    RET

; Modulus (R0 % R1)
; Arguments: R0, R1 
; Return: R2
MOD
    LEA R6, MOD_REG
    STR R0, R6, #0
    STR R1, R6, #1
    STR R3, R6, #3
    STR R4, R6, #4
    STR R5, R6, #5
    STR R7, R6, #7

    JSR DIV
    ADD R2, R4, #0

    LEA R6, MOD_REG
    LDR R0, R6, #0
    LDR R1, R6, #1
    LDR R3, R6, #3
    LDR R4, R6, #4
    LDR R5, R6, #5
    LDR R7, R6, #7

    RET


; Stringify
; Arguments: R0
; Return: R1 (a memory address pointing to the beginning of an array of numbers to print)
; Notes: Only handles positive numbers in range[0,2^15-1==32767]. Sign bit makes this 2^(15-1) instead of 2^(16-1)
STRINGIFY
    ; save registers
    LEA R6, STR_SAVE_REG
    STR R0, R6, #0
    STR R7, R6, #7

    ; Nullify the output array
    LEA R2, STR_OUTPUT_REG
    AND R3, R3, #0
    ADD R3, R3, #5
    AND R4, R3, #0
    NULLIFY_LOOP
        STR R4, R2, #0
        ADD R2, R2, #1
        ADD R3, R3, #-1
        BRzp NULLIFY_LOOP

    ; R1=10
    ; R2=address to put the digit/remainder. We populate STR[REG] from back to front [4,3,2,1,0]
    AND R1, R1, #0
    ADD R1, R1, #10
    LEA R2, STR_OUTPUT_REG
    ADD R2, R2, #5
    STR_LOOP
        JSR DIV ; R3=R0//R1, R4=R0 % R1

        LD R6, ASCII_ZERO
        ADD R4, R4, R6
        STR R4, R2, #0
        ADD R0, R3, #0
        BRz END             ; if the quotient is zero, end
        ADD R2, R2, #-1     ; decrement where in STR_REG we put the modulus the next time
        BR STR_LOOP
    END

    ADD R1, R2, #0

    ; load registers
    LEA R6, STR_SAVE_REG
    LDR R0, R6, #0
    LDR R7, R6, #7

    RET


; Data Section
ASCII_ZERO .FILL x30
NEWLINE    .FILL x0A       ; ASCII value for newline
DIV_REG .BLKW 8
MOD_REG .BLKW 8

; 5 bits for each character
STR_OUTPUT_REG .BLKW 8
STR_SAVE_REG .BLKW 8

STRINGIFY_OP .FILL x2B67
