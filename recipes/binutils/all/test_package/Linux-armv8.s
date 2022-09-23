    .global _start

    .text
_start:
    # write(1, message, 14)
    mov x8, 64                      // system call 64 is write
    mov x0, 1                       // file handle 1 is stdout
    mov x1, message                 // address of string to output
    mov x2, 14                      // number of bytes
    svc 0                           // do syscall into os (supervisor call)

    # exit(0)
    mov x8, 93                      // system call 93 is exit
    mov x0, 0                       // we want return code 0
    svc 0                           // do syscall into os (supervisor call)

    .section .rodata
message:
    .ascii  "Hello, world!\n"
