.ORIG x3000
        AND R1, R1, #0      ; Clear R1, will use as our counter
        LD R3, ASCII_ZERO   ; Load ASCII offset for '0'
        LD R6, THING        ; thingy

LOOP    ADD R0, R3, R1      ; Convert number to ASCII by adding offset
        OUT                 ; Print the character in R0
        LD R0, NEWLINE      ; Load newline character
        OUT                 ; Print newline
        ADD R1, R1, #1      ; Increment counter
        ADD R5, R1, R6    ; Check if counter  - 10 ==0
        BRn LOOP           ; If counter < 10, continue loop
        HALT               ; Stop program

ASCII_ZERO .FILL x30       ; ASCII value for '0'
NEWLINE    .FILL x0A       ; ASCII value for newline
THING      .FILL xFFF0       ; counter

.END