; Print "Hello, Conan"

          global  _start

          extern  WriteFile
          extern  GetStdHandle

          section .data
message:  db      "Hello, Conan", 10

          section .text
_start:                                ;
          sub     rsp, 40              ; reserve 40 bytes for WriteFile and GetStdHandle arguments (5 arguments of 8 bytes each)
          mov     rcx, -11             ; STD_OUTPUT const as argument for GetStdHandle
          call    GetStdHandle         ; invoke GetStdHandle function
          mov     rcx, rax             ; set file handle (cmd handle) in RCX register - first WriteFile function argument
          mov     rdx, message         ; set address of string in RDX register        - second WriteFile function argument
          mov     r8d, 18              ; set string length (in bytes) in R8D register - third WriteFile function argument
          xor     r9, r9               ; clear R9D register                           - fourth WriteFile function argument
          mov     qword [rsp + 32], 0  ; set qword in top of stack to zero state      - fifth WriteFile function argument
          call    WriteFile            ; invoke WriteFile function
          add     rsp, 40              ; restore stack pointer
          syscall