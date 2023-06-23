    .section .rdata,"dr"

output: .ascii "Hello, world!\n"

    .text
    .globl _start

_start:
    # GetStdHandle(STD_OUTPUT_HANDLE)
    mov $-11, %rcx                          # STD_OUTPUT_HANDLE (=COUNOUT$)
    movq __imp_GetStdHandle(%rip), %rax     # Get relocatable address of __imp_GetStdHandle
    call *%rax                              # Retrieve console handle

    # WriteConsoleA($handle, "Hello world!\n", 14, NULL, 0)
    pushq $0                                # lpReserved
    movq $0, %r9                            # lpNumberOfCharsWritten (optional)
    movq $14, %r8                           # nNumberOfCharsToWrite
    leaq output(%rip), %rdx                 # lpBuffer
    movq %rax, %rcx                         # hConsoleOutput
    movq __imp_WriteConsoleA(%rip), %rax    # Get relocatable address of __imp_WriteConsoleA
    call *%rax                              # Write to console

    # ExitProcess(0)
    xorq %rcx, %rcx                         # Return 0 errorcode
    movq __imp_ExitProcess(%rip), %rax      # Get relocatable address of __imp__ExitProcess
    call *%rax                              # Exit process
