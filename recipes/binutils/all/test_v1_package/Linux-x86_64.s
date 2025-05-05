    .global _start

    .text
_start:
    # write(1, message, 14)
    mov $1, %rax                    # system call 1 is write
    mov $1, %rdi                    # file handle 1 is stdout
    mov $message, %rsi              # address of string to output
    mov $14, %rdx                   # number of bytes
    syscall                         # do syscall into os

    # exit(0)
    mov $60, %eax                   # system call 60 is exit
    xor %rdi, %rdi                  # we want return code 0
    syscall                         # do syscall into os

    .section .data

message:
    .ascii  "Hello, world!\n"
