.ORIG x3000

MULT_MSG .STRINGZ "Mutiplication 15x4="
DIV_MSG .STRINGZ "Division 255/5="
MOD_MSG .STRINGZ "Mod 1011%17="
STRINGIFY_MSG .STRINGZ "Print 0x2B67="
FIZZBUZZ_MSG .STRINGZ "FizzBuzz 15:"

MULT_MSG_PTR .FILL MULT_MSG
;DIV_MSG_PTR .FILL DIV_MSG
;MOD_MSG_PTR .FILL MOD_MSG
MULT_REG_PTR .FILL MULT_REG
;DIV_REG_PTR .FILL DIV_REG
;MOD_REG_PTR .FILL MOD_REG

MULT_OP1 .FILL xF
MULT_OP2 .FILL x4
MOD_OP1 .FILL x3F3
MOD_OP2 .FILL x11
DIV_OP1 .FILL xFF
DIV_OP2 .FILL x5

; Multiplication
LD R0, MULT_MSG_PTR
PUTS
LD R0, MULT_OP1
LD R1, MULT_OP2
JSR MULT
AND R0, R0, #0
ADD R0, R2, #0
JSR STRINGIFY
AND R0, R0, #0
ADD R0, R1, #0
PUTS
LD R0, NEWLINE
OUT


; Division
LEA R0, DIV_MSG
PUTS
LD R0, DIV_OP1
LD R1, DIV_OP2
JSR DIV
AND R0, R0, #0
ADD R0, R3, #0
JSR STRINGIFY
AND R0, R0, #0
ADD R0, R1, #0
PUTS
LD R0, NEWLINE
OUT

; Modulus
LEA R0, MOD_MSG
PUTS
LD R0, MOD_OP1
LD R1, MOD_OP2
JSR MOD
AND R0, R0, #0
ADD R0, R2, #0
JSR STRINGIFY
AND R0, R0, #0
ADD R0, R1, #0
PUTS
LD R0, NEWLINE
OUT

; Stringify
LEA R0, STRINGIFY_MSG
PUTS
LD R0, STRINGIFY_OP
JSR STRINGIFY
ADD R0, R1, #0
PUTS
LD R0, NEWLINE
OUT


; FIZZBUZZ
LEA R0, FIZZBUZZ_MSG
PUTS
LD R0, FIZZBUZZ_ARG
JSR FIZZBUZZ

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

; Execute FizzBuzz
; Args: R0
FIZZBUZZ
    LEA R6, FIZZBUZZ_STG
    STR R0, R6, #0
    STR R1, R6, #1
    STR R2, R6, #2
    STR R3, R6, #3
    STR R7, R6, #7

    ; Use R4 as flag
    AND R4, R4, #0

    ; Print Fizz if R0 % 3 == 0
    AND R1, R1, #0
    ADD R1, R1, #3
    JSR MOD

    ADD R2, R2, #0
    BRp NOT_FIZZ
        LEA R0, FIZZ_STR
        PUTS
        ADD R4, R4, #1
    NOT_FIZZ

    ; Print BUZZ if R0 % 5 == 0
    LDR R0, R6, #0
    AND R1, R1, #0
    ADD R1, R1, #5
    JSR MOD

    ADD R2, R2, #0
    BRp NOT_BUZZ
        LEA R0, BUZZ_STR
        PUTS
        ADD R4, R4, #1
    NOT_BUZZ

    ; If R4 !=0, it was not divisible by 3 or 5. 
    ADD R4, R4, #0
    BRp DIVISIBLE
        LDR R0, R6, #0
        JSR STRINGIFY
        ADD R0, R1, #0
        PUTS
    DIVISIBLE

    LD R0, NEWLINE
    OUT

    LEA R6, FIZZBUZZ_STG
    LDR R0, R6, #0
    LDR R1, R6, #1
    LDR R2, R6, #2
    LDR R3, R6, #3
    LDR R7, R6, #7
    RET

; Data Section
ASCII_ZERO .FILL x30
NEWLINE    .FILL x0A       ; ASCII value for newline
MULT_REG .BLKW 8
DIV_REG .BLKW 8
MOD_REG .BLKW 8

; Strings
FIZZBUZZ_STG .BLKW 8
FIZZ_STR .STRINGZ "Fizz"
BUZZ_STR .STRINGZ "Buzz"
FIZZBUZZ_ARG .FILL x0F

; 5 bits for each character
STR_OUTPUT_REG .BLKW 8
STR_SAVE_REG .BLKW 8

STRINGIFY_OP .FILL x2B67

