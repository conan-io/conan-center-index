    .section .rdata,"dr"

output: .ascii "Hello, world!\n"

    .text
    .globl _start

_start:
    # GetStdHandle(STD_OUTPUT_HANDLE)
    pushl $-11                              # STD_OUTPUT_HANDLE (=COUNOUT$)
    call _GetStdHandle                      # Retrieve console handle

    # WriteConsoleA($handle, output, 14, NULL, 0)
    pushl $0                                # lpReserved
    pushl $0                                # lpNumberOfCharsWritten (optional)
    pushl $14                               # nNumberOfCharsToWrite
    pushl $output                           # lpBuffer
    pushl %eax                              # hConsoleOutput
    call _WriteConsoleA                     # Write to console

    # ExitProcess(0)
    pushl $0                                # Return 0 errorcode
    call _ExitProcess                       # Exit process
