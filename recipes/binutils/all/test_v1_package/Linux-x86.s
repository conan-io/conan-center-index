    .global _start

    .text
_start:
    # write(1, message, 14)
    mov $4, %eax                    # system call 4 is write
    mov $1, %ebx                    # file handle 1 is stdout
    mov $message, %ecx              # address of string to output
    mov $14, %edx                   # number of bytes
    int $0x80                       # do syscall into os

    # exit(0)
    mov $1, %eax                    # system call 1 is exit
    xor %ebx, %ebx                  # we want return code 0
    int $0x80                       # do syscall into os

    .data

message:
    .ascii  "Hello, world!\n"
