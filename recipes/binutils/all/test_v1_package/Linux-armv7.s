    .arm
    .arch armv7-a

    .global _start

    .text
_start:
    # write(1, message, 14)
    mov r7, #4                      // system call 4 is write
    mov r0, #1                      // file handle 1 is stdout
    adr r1, message                 // address of string to output
    mov r2, #14                     // number of bytes
    swi #0                          // do syscall into os (supervisor call)

    # exit(0)
    mov r7, #1                      // system call 1 is exit
    mov r0, #0                      // we want return code 0
    swi #0                          // do syscall into os (supervisor call)

    .align 2

message:
    .ascii  "Hello, world!\n"
