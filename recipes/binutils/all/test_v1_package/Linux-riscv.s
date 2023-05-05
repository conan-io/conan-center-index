    .global _start

    .text
_start:
    # write(1, message, 14)
    addi a7, x0, 64                  # system call 64 is write
    addi a0, x0, 1                  # file handle 1 is stdout
    la a1, message                  # address of string to output
    addi a2, x0, 14                 # number of bytes
    ecall                           # do syscall into os (environment call)

    # exit(0)
    addi a7, x0, 93                 # system call 93 is exit
    addi a0, x0, 0                  # we want return code 0
    ecall                           # do syscall into os (environment call)

    .data
message:
    .ascii  "Hello, world!\n"
